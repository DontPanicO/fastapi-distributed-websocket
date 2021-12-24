from typing import Optional, Any, Callable, NoReturn
from collections.abc import AsyncIterator, Awaitable, Coroutine

from fastapi import WebSocket, WebSocketDisconnect, status


class Connection:

    def __init__(self, websocket: WebSocket, conn_id: str, topic: Optional[str] = None) -> NoReturn:
        self.websocket: WebSocket = websocket
        self.id: str = conn_id
        self.topic: Optional[str] = topic
        self.accept: Callable[[], Coroutine[Any, Any, None]] = websocket.accept
        self.send_json: Callable[[Any, str], Coroutine[Any, Any, None]] = websocket.send_json
        self.iter_json: Callable[[], AsyncIterator] = websocket.iter_json
    
    async def close(self, code: int = status.WS_1000_NORMAL_CLOSURE) -> NoReturn:
        await self.websocket.close(code)
