from typing import AsyncIterator, Optional, Any, Callable, Awaitable, NoReturn

from fastapi import WebSocket, WebSocketDisconnect


class Connection:

    def __init__(self, websocket: WebSocket, conn_id: str, topic: Optional[str] = None) -> NoReturn:
        self.websocket: WebSocket = websocket
        self.id: str = conn_id
        self.topic: Optional[str] = topic
        self.accept: Callable[[], Awaitable] = websocket.accept
        self.send_json: Callable[[Any, str], Awaitable] = websocket.send_json
        self.iter_json: Callable[[], Awaitable] = websocket.iter_json
    
    async def close(self) -> NoReturn:
        await self.websocket.close()
