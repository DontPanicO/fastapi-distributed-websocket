import pytest

from starlette import status
from starlette.types import Receive, Scope, Send
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from distributed_websocket._connection import Connection


def test_connection_send(test_client_factory: TestClient) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        await connection.send_json({'your_id': connection.id})

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}
