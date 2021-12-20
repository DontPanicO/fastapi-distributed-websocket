from typing import AsyncIterator, Optional, Any

from fastapi import WebSocket, WebSocketDisconnect


class Connection:

    def __init__(self, websocket: WebSocket, conn_id: str, topic: Optional[str] = None) -> None:
        self.websocket: WebSocket = websocket
        self.id: str = conn_id
        self.topic: Optional[str] = topic
        self.accept = websocket.accept
        self.send_json = websocket.send_json
        self.iter_json = websocket.iter_json
    
    async def close(self) -> None:
        await self.websocket.close()
