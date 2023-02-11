from collections.abc import Callable

import pytest
from starlette import status
from starlette.testclient import TestClient
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from distributed_websocket._connection import Connection


def test_connection_send(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        await connection.send_json({'your_id': connection.id})

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}


def test_connection_iter_json(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        async for data in connection.iter_json():
            await connection.send_json({'your_id': connection.id, 'msg': data})

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        websocket.send_json({'msg': 'hello'})
        data = websocket.receive_json()
        assert data == {'your_id': 'test', 'msg': {'msg': 'hello'}}


def test_connection_iter(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        async for msg in connection:
            if msg is not None:
                await connection.send_json(
                    {'your_id': connection.id, 'msg': {**msg.data}}
                )

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        websocket.send_json({'msg': 'hello'})
        data = websocket.receive_json()
        assert data == {'error': 'Invalid message type: None'}
        websocket.send_json({'type': 'broadcast', 'msg': 'hello'})
        data2 = websocket.receive_json()
        assert data2 == {'your_id': 'test', 'msg': {'msg': 'hello'}}
