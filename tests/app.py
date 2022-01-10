from typing import Optional, Any, NoReturn
from collections.abc import AsyncIterator, Awaitable, Coroutine

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, Depends
from distributed_websocket import (
    WebSocketManager,
    Connection,
    WebSocketOAuth2PasswordBearer,
)


fake_db = {'users': [{'id': 1, 'username': 'johndoe', 'password': 'secret'}]}

app = FastAPI()
manager = WebSocketManager('test-channel', 'memory://')

ws_oauth2_scheme = WebSocketOAuth2PasswordBearer(token_url='/token')


def fake_encode(data: Any) -> Any:
    pass


def fake_decode(token: str) -> Any:
    pass


async def get_token(websocket: WebSocket) -> Optional[str]:
    return await ws_oauth2_scheme(websocket)


async def get_current_user(token: Optional[str] = Depends(get_token)):
    if token is None:
        return None
    return fake_db['users'][fake_decode(token)]


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
