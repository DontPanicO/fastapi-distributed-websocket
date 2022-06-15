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
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
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
manager = WebSocketManager('test-channel', 'redis://redis')

ws_oauth2_scheme = WebSocketOAuth2PasswordBearer(token_url='/token')


def get_user_by_username(username: str) -> Any:
    return next((usr for usr in fake_db['users'] if usr['username'] == username), None)


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


async def get_current_user(
    token: Optional[str] = Depends(ws_oauth2_scheme),
) -> Optional[Any]:
    if token is None:
        return None
    return fake_db['users'][fake_decode(token)]


@app.on_event('startup')
async def startup() -> Coroutine[Any, Any, NoReturn]:
    await manager.startup()


@app.on_event('shutdown')
async def shutdown() -> Coroutine[Any, Any, NoReturn]:
    await manager.shutdown()


@app.post('/token', response_class=JSONResponse)
def token(data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = authenticate(data.username, data.password)
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
            await connection.send_json(message)
    except WebSocketDisconnect:
        manager.remove_connection(connection)


@app.websocket('/ws/{conn_id}')
async def websocket_receive_endpoint(
    websocket: WebSocket, conn_id: str, user: Optional[Any] = Depends(get_current_user)
) -> Coroutine[Any, Any, NoReturn]:
    connection = await manager.new_connection(websocket, conn_id)
    try:
        async for message in connection.iter_json():
            await manager.receive(connection, message)
    except WebSocketDisconnect:
        manager.remove_connection(connection)
