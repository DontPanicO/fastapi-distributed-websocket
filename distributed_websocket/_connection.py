from typing import Any, Callable
from collections.abc import AsyncIterator, Coroutine

from fastapi import WebSocket, status


class Connection:
    def __init__(
        self, websocket: WebSocket, conn_id: str, topic: str | None = None
    ) -> None:
        self.websocket: WebSocket = websocket
        self.id: str = conn_id
        self.topics: set = {topic} if topic else set()
        self.accept: Callable[
            [str | None], Coroutine[Any, Any, None]
        ] = websocket.accept
        self.receive_json: Callable[
            [str], Coroutine[Any, Any, Any]
        ] = websocket.receive_json
        self.send_json: Callable[
            [Any, str], Coroutine[Any, Any, None]
        ] = websocket.send_json
        self.iter_json: Callable[[], AsyncIterator] = websocket.iter_json

    async def __aiter__(self) -> AsyncIterator:
        return self.iter_json()

    async def close(
        self, code: int = status.WS_1000_NORMAL_CLOSURE
    ) -> Coroutine[Any, Any, None]:
        await self.websocket.close(code)
