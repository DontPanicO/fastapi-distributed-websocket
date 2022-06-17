import asyncio
from typing import Iterator, Any
from collections.abc import Coroutine

from fastapi import WebSocket, status

from ._connection import Connection
from .utils import clear_task, is_valid_broker, serialize
from ._types import BrokerT
from ._message import validate_incoming_message, untag_broker_message, Message
from ._broker import create_broker
from ._matching import matches
from ._subscriptions import is_subscription_message, handle_subscription_message
from ._exception_handlers import send_error_message
from ._decorators import ahandle
from ._exceptions import WebSocketException


def _init_broker(url: str, broker_class: Any | None = None, **kwargs) -> BrokerT:
    if broker_class:
        assert is_valid_broker(
            broker_class
        ), 'Invalid broker class. Use distributed_websocket.utils.is_valid_broker to check if your broker_class is valid.'
        return broker_class(**kwargs)
    return create_broker(url, **kwargs)


class WebSocketManager:
    def __init__(
        self,
        broker_channel,
        broker_url: str | None = None,
        broker_class: Any | None = None,
        **kwargs,
    ) -> None:
        self.active_connections: list[Connection] = []
        self._send_tasks: list[asyncio.Task] = []
        self._main_task: asyncio.Task | None = None
        self.broker: BrokerT | None = _init_broker(broker_url, broker_class, **kwargs)
        self.broker_channel: str = broker_channel

    async def __aenter__(self) -> Coroutine[Any, Any, 'WebSocketManager']:
        await self.startup()
        return self

    async def __aexit__(
        self, exc_type, exc_val, exc_tb
    ) -> Coroutine[Any, Any, None]:
        await self.shutdown()

    def __iter__(self) -> Iterator:
        return self.active_connections.__iter__()

    async def _connect(self, connection: Connection) -> Coroutine[Any, Any, None]:
        await connection.accept()
        self.active_connections.append(connection)

    def _disconnect(self, connection: Connection) -> None:
        self.active_connections.remove(connection)

    async def new_connection(
        self, websocket: WebSocket, conn_id: str, topic: str | None = None
    ) -> Coroutine[Any, Any, Connection]:
        connection = Connection(websocket, conn_id, topic)
        await self._connect(connection)
        return connection

    async def close_connection(
        self, connection: Connection, code: int = status.WS_1000_NORMAL_CLOSURE
    ) -> Coroutine[Any, Any, None]:
        await connection.close(code)
        self._disconnect(connection)

    def remove_connection(self, connection: Connection) -> None:
        '''
        Use it after a `WebSocketDisconnect` exception.
        If `WebSocketDisconnect` exception has been raised, we do not
        need to call `connection.close()`
        '''
        self._disconnect(connection)

    async def _set_conn_id(
        self, connection: Connection, conn_id: str
    ) -> Coroutine[Any, Any, None]:
        connection.conn_id = conn_id
        await connection.send_json({'type': 'set_conn_id', 'conn_id': conn_id})

    def set_conn_id(self, connection: Connection, conn_id: str) -> None:
        self._send_tasks.append(
            asyncio.create_task(self._set_conn_id(connection, conn_id))
        )

    async def _send(self, topic: str, message: Any) -> Coroutine[Any, Any, None]:
        for connection in self.active_connections:
            if matches(topic, connection.topics):
                await connection.send_json(message)

    def send(self, topic: str, message: Any) -> None:
        self._send_tasks.append(asyncio.create_task(self._send(topic, message)))

    async def _broadcast(self, message: Any) -> Coroutine[Any, Any, None]:
        for connection in self.active_connections:
            await connection.send_json(message)

    def broadcast(self, message: Any) -> None:
        self._send_tasks.append(asyncio.create_task(self._broadcast(message)))

    async def _send_by_conn_id(
        self, conn_id: str, message: Any
    ) -> Coroutine[Any, Any, None]:
        for connection in self.active_connections:
            if connection.id == conn_id:
                await connection.send_json(message)
                break

    async def _send_multi_by_conn_id(
        self, conn_ids: list[str], message: Any
    ) -> Coroutine[Any, Any, None]:
        for connection in self.active_connections:
            if connection.id in conn_ids:
                await connection.send_json(message)

    def send_by_conn_id(self, conn_id: str | list[str], message: Any) -> None:
        if isinstance(conn_id, list):
            self._send_tasks.append(
                asyncio.create_task(self._send_multi_by_conn_id(conn_id, message))
            )
        else:
            self._send_tasks.append(
                asyncio.create_task(self._send_by_conn_id(conn_id, message))
            )

    def send_multi_by_conn_id(self, conn_ids: list[str], message: Any) -> None:
        # to be removed
        self._send_tasks.append(
            asyncio.create_task(self._send_multi_by_conn_id(conn_ids, message))
        )

    def send_msg(self, message: Message) -> None:
        if message.typ == 'broadcast':
            self.broadcast(message.data)
        elif message.typ == 'send_by_conn_id':
            self.send_by_conn_id(message.conn_id, message.data)
        else:
            self.send(message.topic, message.data)

    async def _publish_to_broker(self, message: Any) -> Coroutine[Any, Any, None]:
        await self.broker.publish(self.broker_channel, message)

    async def _handle_client_message(
        self, connection: Connection, message: Message
    ) -> Coroutine[Any, Any, None]:
        if is_subscription_message(message):
            handle_subscription_message(connection, message)
        else:
            await self._publish_to_broker(serialize(message))

    @ahandle(WebSocketException, send_error_message)
    async def receive(
        self, connection: Connection, message: Any
    ) -> Coroutine[Any, Any, None]:
        validate_incoming_message(message)
        await self._handle_client_message(
            connection, Message.from_client_message(data=message)
        )

    async def _next_broker_message(self) -> Coroutine[Any, Any, Message]:
        return await self.broker.get_message()

    async def _broker_listener(self) -> Coroutine[Any, Any, None]:
        while True:
            message = await self._next_broker_message()
            if message is not None:
                self.send_msg(message)

    async def startup(self) -> Coroutine[Any, Any, None]:
        await self.broker.connect()
        await self.broker.subscribe(self.broker_channel)
        self._main_task = asyncio.create_task(self._broker_listener())

    async def shutdown(self) -> Coroutine[Any, Any, None]:
        for task in self._send_tasks:
            clear_task(task)
        for connection in self.active_connections:
            await self.close_connection(connection, code=status.WS_1012_SERVICE_RESTART)
        clear_task(self._main_task)
        await self.broker.disconnect()
