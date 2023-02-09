from collections.abc import Callable

import pytest
from starlette import status
from starlette.types import Receive, Scope, Send
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from distributed_websocket._auth import WebSocketOAuth2PasswordBearer


def test_oauth2_password_bearer(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        auth = WebSocketOAuth2PasswordBearer('http://testserver/v1/access_token/')
        token = await auth(websocket)
        await websocket.send_json({'your_id': token})

    client = test_client_factory(app)
    with client.websocket_connect(
        '/', headers={'Authorization': 'Bearer test'}
    ) as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}


def test_oauth2_password_bearer_no_auth(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        auth = WebSocketOAuth2PasswordBearer('http://testserver/v1/access_token/')
        token = await auth(websocket)
        with pytest.raises(RuntimeError):
            await websocket.send_json({'your_id': token})

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_json()
