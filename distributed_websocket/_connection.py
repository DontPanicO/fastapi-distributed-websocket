from typing import Optional, Any, Callable, NoReturn
from collections.abc import AsyncIterator, Awaitable, Coroutine

from fastapi import WebSocket, WebSocketDisconnect, status


class Connection:
    def __init__(
        self, websocket: WebSocket, conn_id: str, topic: Optional[str] = None
    ) -> NoReturn:
        self.websocket: WebSocket = websocket
        self.id: str = conn_id
        self.topic: Optional[str] = topic
        self.accept: Callable[[], Coroutine[Any, Any, NoReturn]] = websocket.accept
        self.send_json: Callable[
            [Any, str], Coroutine[Any, Any, NoReturn]
        ] = websocket.send_json
        self.iter_json: Callable[[], AsyncIterator] = websocket.iter_json

    async def close(
        self, code: int = status.WS_1000_NORMAL_CLOSURE
    ) -> Coroutine[Any, Any, NoReturn]:
        await self.websocket.close(code)
