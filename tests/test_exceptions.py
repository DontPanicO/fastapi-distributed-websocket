from collections.abc import Callable

import pytest
from starlette import status
from starlette.types import Receive, Scope, Send
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from distributed_websocket._connection import Connection
from distributed_websocket._exceptions import WebSocketException


def test_websocket_exception(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        try:
            raise WebSocketException('test', connection=connection)
        except WebSocketException as e:
            assert e.message == 'test'
            assert e.connection == connection
        else:
            assert False

    test_client = test_client_factory(app)
    with test_client.websocket_connect('/') as ws:
        pass
