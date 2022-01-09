import asyncio
import json
from urllib.parse import urlparse
from typing import Optional, Any, NoReturn, Union
from collections.abc import Coroutine

from aioredis import Redis
from fastapi import WebSocket, WebSocketDisconnect, status

from ._connection import Connection
from .utils import clear_task, is_valid_broker
from .types import BrokerT
from ._message import tag_client_message, untag_broker_message
from ._inmemory_broker import InMemoryBroker


def _init_broker(url: str, broker_class: Optional[Any] = None, **kwargs) -> BrokerT:
    if broker_class:
        assert is_valid_broker(
            broker_class
        ), 'Invalid broker class. Use distributed_websocket.utils.is_valid_broker to check if your broker_class is valid.'
        return broker_class(**kwargs)
    parsed_url = urlparse(url)
    if parsed_url.scheme == 'memory':
        return InMemoryBroker()
    elif parsed_url.scheme == 'redis':
        return Redis.from_url(url).pubsub()
    raise ValueError('Unsupported broker scheme')


class WebSocketManager:
    def __init__(
        self,
        broker_channel,
        broker_url: Optional[str] = None,
        broker_class: Optional[Any] = None,
        **kwargs,
    ) -> NoReturn:
        self.active_connections: list[Connection] = []
        self._send_tasks: list[asyncio.Task] = []
        self._main_task: Optional[asyncio.Task] = None
        self.broker: Optional[BrokerT] = _init_broker(
            broker_url, broker_class, **kwargs
        )
        self.broker_channel: str = broker_channel

    async def __aenter__(self) -> Coroutine[Any, Any, 'WebSocketManager']:
        await self.startup()
        return self

    async def __aexit__(
        self, exc_type, exc_val, exc_tb
    ) -> Coroutine[Any, Any, NoReturn]:
        await self.shutdown()

    async def _connect(self, connection: Connection) -> Coroutine[Any, Any, NoReturn]:
        await connection.accept()
        self.active_connections.append(connection)

    def _disconnect(self, connection: Connection) -> NoReturn:
        self.active_connections.remove(connection)

    async def new_connection(
        self, websocket: WebSocket, conn_id: str, topic: Optional[str] = None
    ) -> Coroutine[Any, Any, Connection]:
        connection = Connection(websocket, conn_id, topic)
        await self._connect(connection)
        return connection

    async def remove_connection(
        self, connection: Connection, code: int = status.WS_1000_NORMAL_CLOSURE
    ) -> Coroutine[Any, Any, NoReturn]:
        await connection.close(code)
        self._disconnect(connection)

    def raw_remove_connection(self, connection: Connection) -> NoReturn:
        """
        Use it after a `WebSocketDisconnect` exception.
        If `WebSocketDisconnect` exception has been raised, we do not
        need to call `connection.close()`
        """
        self._disconnect(connection)

    async def _send(self, topic: str, message: Any) -> Coroutine[Any, Any, NoReturn]:
        for connection in self.active_connections:
            if connection.topic == topic:
                await connection.send_json(message)

    def send(self, topic: str, message: Any) -> NoReturn:
        self._send_tasks.append(asyncio.create_task(self._send(topic, message)))

    async def _to_broker(self, message: Any) -> Coroutine[Any, Any, NoReturn]:
        await self.broker.publish(self.broker_channel, message)

    async def receive(self, message: Any) -> Coroutine[Any, Any, NoReturn]:
        msg = tag_client_message(message)
        await self._to_broker(msg)

    async def _next_broker_message(self) -> Coroutine[Any, Any, Union[dict, Any]]:
        broker_message: dict[str, str] = await self.broker.get_message(
            ignore_subscribe_messages=True
        )
        return untag_broker_message(broker_message['data'])

    async def _from_broker(self) -> Coroutine[Any, Any, NoReturn]:
        while True:
            typ, topic, message = await self._next_broker_message()
            self.send_msg(message, typ, topic)

    async def _broadcast(self, message: Any) -> Coroutine[Any, Any, NoReturn]:
        for connection in self.active_connections:
            await connection.send_json(message)

    def broadcast(self, message: Any) -> NoReturn:
        self._send_tasks.append(asyncio.create_task(self._broadcast(message)))

    def send_msg(
        self, message: Any, typ: Optional[str] = None, topic: Optional[str] = None
    ) -> NoReturn:
        if not topic and typ == 'broadcast':
            self.broadcast(message)
        else:
            self.send(topic, message)

    async def startup(self) -> Coroutine[Any, Any, NoReturn]:
        await self.broker.subscribe(self.broker_channel)
        self._main_task = asyncio.create_task(self._from_broker())

    async def shutdown(self) -> Coroutine[Any, Any, NoReturn]:
        for task in self._send_tasks:
            clear_task(task)
        for connection in self.active_connections:
            await self.remove_connection(
                connection, code=status.WS_1012_SERVICE_RESTART
            )
        clear_task(self._main_task)
