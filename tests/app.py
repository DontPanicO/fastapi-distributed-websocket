from typing import Optional, Any, NoReturn
from collections.abc import AsyncIterator, Awaitable, Coroutine

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    status,
    Depends,
    HTTPException,
)
from distributed_websocket import (
    WebSocketManager,
    Connection,
    WebSocketOAuth2PasswordBearer,
)


fake_db = {
    'users': [
        {'id': 1, 'username': 'johndoe', 'password': 'secret'},
        {'id': 2, 'username': 'samsmith', 'password': 'secret2'},
    ]
}

app = FastAPI()
manager = WebSocketManager('test-channel', 'memory://')

ws_oauth2_scheme = WebSocketOAuth2PasswordBearer(token_url='/token')


def get_user_by_username(username: str) -> Any:
    return fake_db['users'].get(username, None)


def check_password(user: Any, password: str) -> bool:
    if user is not None:
        return user['password'] == password


def authenticate(username: str, password: str) -> Any:
    user = get_user_by_username(username)
    if check_password(user, password):
        return user


def fake_encode(user: Any) -> Any:
    return str(user['id'])


def fake_decode(token: str) -> Any:
    return int(token)


async def get_token(websocket: WebSocket) -> Optional[str]:
    return await ws_oauth2_scheme(websocket)


async def get_current_user(token: Optional[str] = Depends(get_token)) -> Any:
    if token is None:
        return None
    return fake_db['users'][fake_decode(token)]


@app.on_event('startup')
async def startup() -> Coroutine[Any, Any, NoReturn]:
    await manager.startup()


@app.on_event('shutdown')
async def shutdown() -> Coroutine[Any, Any, NoReturn]:
    await manager.shutdown()


@app.post('/token')
def token(username: str, password: str) -> Any:
    user = authenticate(username, password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {'access_token': fake_encode(user)}


@app.websocket('/ws/broadcast/{conn_id}')
async def websocket_broadcast_endpoint(
    websocket: WebSocket, conn_id: str
) -> Coroutine[Any, Any, NoReturn]:
    connection = await manager.new_connection(websocket, conn_id)
    try:
        async for message in connection.iter_json():
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.raw_remove_connection(connection)


@app.websocket('/ws/{conn_id}')
async def websocket_broadcast_endpoint(
    websocket: WebSocket, conn_id: str
) -> Coroutine[Any, Any, NoReturn]:
    connection = await manager.new_connection(websocket, conn_id)
    try:
        async for message in connection.iter_json():
            await manager.receive(message)
    except WebSocketDisconnect:
        manager.raw_remove_connection(connection)


@app.websocket('ws/auth/{conn_id}')
async def websocket_auth_endpoint(
    websocket: WebSocket, conn_id: str, *, user: Any = Depends(get_current_user)
) -> Coroutine[Any, Any, NoReturn]:
    connection = await manager.new_connection(websocket, conn_id)
    try:
        async for message in connection.iter_json():
            await manager.receive(message)
    except WebSocketDisconnect:
        manager.raw_remove_connection(connection)
