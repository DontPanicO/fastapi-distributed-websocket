from typing import Optional, Any
from collections.abc import AsyncIterator, Awaitable, Coroutine

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    status,
    Depends,
    HTTPException,
)
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from distributed_websocket import WebSocketProxy


app = FastAPI()


WS_TARGET_ENDPOINT = 'ws://testapp:8000/ws/broadcast/myid23'

@app.websocket('/ws')
async def websocket_proxy(websocket: WebSocket):
    await websocket.accept()
    ws_proxy = WebSocketProxy(websocket, WS_TARGET_ENDPOINT)
    await ws_proxy()
