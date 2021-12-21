import asyncio
from fastapi import WebSocket, WebSocketDisconnect

from ._connection import Connection
from .utils import clear_task


class WebSocketManager:
    def __init__(self):
        self.active_connections: list[Connection] = []
        self._publish_tasks: list[asyncio.Task] = []

    async def _connect(self, connection: Connection) -> None:
        await connection.accept()
        self.active_connections.append(connection)

    def _disconnect(self, connection: Connection) -> None:
        self.active_connections.remove(connection)

    async def new_connection(
        self, websocket: WebSocket, conn_id: str, topic: Optional[str] = None
    ) -> Connection:
        connection = Connection(websocket, conn_id, topic)
        await self._connect(connection)
        return connection

    async def remove_connection(self, connection: Connection) -> None:
        self._disconnect(connection)
        await self.broadcast({'type': 'disconnect', 'id': connection.id})

    async def _publish(self, topic: str, message: Any) -> None:
        for connection in self.active_connections:
            if connection.topic == topic:
                await connection.send_json(message)

    def publish(self, topic: str, message: Any) -> None:
        self._publish_tasks.append(asyncio.create_task(self._publish(topic, message)))

    async def _to_broker(self, message: Any) -> None:
        pass

    async def broadcast(self, message: Any) -> None:
        for connection in self.active_connections:
            await connection.send_json(message)

    async def shutdown(self) -> None:
        for task in self._publish_tasks:
            clear_task(task)
        for connection in self.active_connections:
            await connection.close()
