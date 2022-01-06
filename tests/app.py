from typing import Optional, Any, NoReturn
from collections.abc import AsyncIterator, Awaitable, Coroutine

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from distributed_websocket import (
    WebSocketManager,
    Connection,
    WebSocketOAuth2PasswordBearer,
)

app = FastAPI()
manager = WebSocketManager('test-channel', 'memory://')


@app.on_event('startup')
async def startup():
    await manager.startup()


@app.on_event('shutdown')
async def shutdown():
    await manager.shutdown()


@app.websocket('/ws/{conn_id}')
async def websocket_endpoint(
    websocket: WebSocket, conn_id: str
) -> Coroutine[Any, Any, NoReturn]:
    connection = await manager.new_connection(websocket, conn_id)
    try:
        async for message in connection.iter_json():
            print(message)
            await manager.receive(message)
    except WebSocketDisconnect:
        manager.raw_remove_connection(connection)
