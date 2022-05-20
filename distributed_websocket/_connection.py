from typing import Any, Callable, NoReturn
from collections.abc import AsyncIterator, Coroutine

from fastapi import WebSocket, status


class Connection:
    def __init__(
        self, websocket: WebSocket, conn_id: str, topic: str | None = None
    ) -> NoReturn:
        self.websocket: WebSocket = websocket
        self.id: str = conn_id
        self.topics: set = {topic} if topic else {}
        self.accept: Callable[
            [str | None], Coroutine[Any, Any, NoReturn]
        ] = websocket.accept
        self.send_json: Callable[
            [Any, str], Coroutine[Any, Any, NoReturn]
        ] = websocket.send_json
        self.iter_json: Callable[[], AsyncIterator] = websocket.iter_json

    async def __aiter__(self) -> AsyncIterator:
        return self.iter_json()

    async def close(
        self, code: int = status.WS_1000_NORMAL_CLOSURE
    ) -> Coroutine[Any, Any, NoReturn]:
        await self.websocket.close(code)
