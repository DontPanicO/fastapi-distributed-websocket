import asyncio
from collections.abc import Callable, Coroutine, Iterator
from typing import Any, TypeVar

from fastapi import WebSocket, status

from ._broker import create_broker
from ._connection import Connection
from ._decorators import ahandle
from ._exception_handlers import send_error_message
from ._exceptions import WebSocketException
from ._matching import matches
from ._message import Message
from ._subscriptions import (
    handle_subscription_message,
    is_subscription_message,
)
from ._types import BrokerT
from .utils import clear_task, is_valid_broker, serialize

T = TypeVar('T')


def _init_broker(
    url: str, broker_class: Any | None = None, **kwargs
) -> BrokerT:
    if broker_class:
        assert is_valid_broker(
            broker_class
        ), 'Invalid broker class. Use distributed_websocket.utils.is_valid_broker to check if your broker_class is valid.'  # noqa: E501
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
        self.broker: BrokerT | None = _init_broker(
            broker_url, broker_class, **kwargs
        )
        self.broker_channel: str = broker_channel

    async def __aenter__(self) -> 'WebSocketManager':
        await self.startup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.shutdown()

    def __iter__(self) -> Iterator:
        return self.active_connections.__iter__()

    async def _connect(self, connection: Connection) -> None:
        await connection.accept()
        self.active_connections.append(connection)

    def _disconnect(self, connection: Connection) -> None:
        self.active_connections.remove(connection)

    async def new_connection(
        self, websocket: WebSocket, conn_id: str, topic: str | None = None
    ) -> Connection:
        connection = Connection(websocket, conn_id, topic)
        await self._connect(connection)
        return connection

    async def close_connection(
        self, connection: Connection, code: int = status.WS_1000_NORMAL_CLOSURE
    ) -> None:
        await connection.close(code)
        self._disconnect(connection)

    def remove_connection(self, connection: Connection) -> None:
        '''
        Use it after a `WebSocketDisconnect` exception.
        If `WebSocketDisconnect` exception has been raised, we do not
        need to call `connection.close()`
        '''
        self._disconnect(connection)

    async def _set_conn_id(self, connection: Connection, conn_id: str) -> None:
        connection.id = conn_id
        await connection.send_json({'type': 'set_conn_id', 'conn_id': conn_id})

    def set_conn_id(self, connection: Connection, conn_id: str) -> None:
        self._send_tasks.append(
            asyncio.create_task(self._set_conn_id(connection, conn_id))
        )

    async def _send(self, message: Message) -> None:
        for connection in self.active_connections:
            if matches(message.topic, connection.topics):
                await connection.send_json(message.data)

    def send(self, message: Message) -> None:
        self._send_tasks.append(asyncio.create_task(self._send(message)))

    async def _broadcast(self, message: Message) -> None:
        for connection in self.active_connections:
            await connection.send_json(message.data)

    def broadcast(self, message: Message) -> None:
        self._send_tasks.append(asyncio.create_task(self._broadcast(message)))

    async def _send_by_conn_id(self, message: Message) -> None:
        for connection in self.active_connections:
            if connection.id == message.conn_id:
                await connection.send_json(message.data)
                break

    async def _send_multi_by_conn_id(self, message: Message) -> None:
        for connection in self.active_connections:
            if connection.id in message.conn_id:
                await connection.send_json(message.data)

    def send_by_conn_id(self, message: Message) -> None:
        if isinstance(message.conn_id, list):
            self._send_tasks.append(
                asyncio.create_task(self._send_multi_by_conn_id(message))
            )
        else:
            self._send_tasks.append(
                asyncio.create_task(self._send_by_conn_id(message))
            )

    def _get_outgoing_message_handler(
        self, message: Message
    ) -> Callable[[Message], T | Coroutine[Any, Any, T]]:
        return getattr(self, message.typ, self.send)

    def send_msg(self, message: Message) -> None:
        self._get_outgoing_message_handler(message)(message)

    async def _publish_to_broker(self, message: Any) -> None:
        await self.broker.publish(self.broker_channel, message)

    @ahandle(WebSocketException, send_error_message)
    async def receive(self, connection: Connection, message: Message) -> None:
        if is_subscription_message(message):
            handle_subscription_message(connection, message)
        else:
            await self._publish_to_broker(serialize(message))

    async def _next_broker_message(self) -> Message:
        return await self.broker.get_message()

    async def _broker_listener(self) -> None:
        while True:
            message = await self._next_broker_message()
            if message is not None:
                self.send_msg(message)

    async def startup(self) -> None:
        await self.broker.connect()
        await self.broker.subscribe(self.broker_channel)
        self._main_task = asyncio.create_task(self._broker_listener())

    async def shutdown(self) -> None:
        for task in self._send_tasks:
            clear_task(task)
        for connection in self.active_connections:
            await self.close_connection(
                connection, code=status.WS_1012_SERVICE_RESTART
            )
        clear_task(self._main_task)
        await self.broker.disconnect()
