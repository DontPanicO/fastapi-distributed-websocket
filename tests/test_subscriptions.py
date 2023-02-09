from collections.abc import Callable

import pytest
from starlette import status
from starlette.types import Receive, Scope, Send
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from distributed_websocket._connection import Connection
from distributed_websocket._subscriptions import (
    subscribe,
    unsubscribe,
    handle_subscription_message,
    is_subscription_message,
)
from distributed_websocket._message import Message
from distributed_websocket._exceptions import InvalidSubscriptionMessage


def test_subscriptions_01(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        await connection.send_json({'your_id': connection.id})
        async for data in connection.iter_json():
            if data['type'] == 'subscribe':
                subscribe(connection, Message.from_client_message(data=data))
        assert connection.topics == {'test/1'}

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}
        websocket.send_json({'type': 'subscribe', 'topic': 'test/1', 'conn_id': 'test'})


def test_subscriptions_02(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        await connection.send_json({'your_id': connection.id})
        async for data in connection.iter_json():
            if data['type'] == 'subscribe':
                subscribe(connection, Message.from_client_message(data=data))
        assert connection.topics == {'test/1', 'test/2'}

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}
        websocket.send_json({'type': 'subscribe', 'topic': 'test/1', 'conn_id': 'test'})
        websocket.send_json({'type': 'subscribe', 'topic': 'test/2', 'conn_id': 'test'})


def test_subscriptions_03(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        await connection.send_json({'your_id': connection.id})
        async for data in connection.iter_json():
            if data['type'] == 'subscribe':
                with pytest.raises(InvalidSubscriptionMessage):
                    subscribe(connection, Message.from_client_message(data=data))
        assert connection.topics == set()

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}
        websocket.send_json({'type': 'subscribe', 'topic': 'test', 'conn_id': 'test'})


def test_subscriptions_04(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        await connection.send_json({'your_id': connection.id})
        async for data in connection.iter_json():
            if data['type'] == 'subscribe':
                subscribe(connection, Message.from_client_message(data=data))
            elif data['type'] == 'unsubscribe':
                unsubscribe(connection, Message.from_client_message(data=data))
        assert connection.topics == set()

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}
        websocket.send_json({'type': 'subscribe', 'topic': 'test/1', 'conn_id': 'test'})
        websocket.send_json(
            {'type': 'unsubscribe', 'topic': 'test/1', 'conn_id': 'test'}
        )


def test_subscriptions_05(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        await connection.send_json({'your_id': connection.id})
        async for data in connection.iter_json():
            if data['type'] == 'subscribe':
                subscribe(connection, Message.from_client_message(data=data))
            elif data['type'] == 'unsubscribe':
                unsubscribe(connection, Message.from_client_message(data=data))
        assert connection.topics == {'test/2'}

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}
        websocket.send_json({'type': 'subscribe', 'topic': 'test/1', 'conn_id': 'test'})
        websocket.send_json({'type': 'subscribe', 'topic': 'test/2', 'conn_id': 'test'})
        websocket.send_json(
            {'type': 'unsubscribe', 'topic': 'test/1', 'conn_id': 'test'}
        )


def test_subscriptions_06(
    test_client_factory: Callable[[Callable[[Scope, Receive, Send], None]], TestClient]
):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        connection = Connection(websocket, 'test')
        await connection.send_json({'your_id': connection.id})
        async for data in connection.iter_json():
            if is_subscription_message(m := Message.from_client_message(data=data)):
                handle_subscription_message(connection, m)
        assert connection.topics == {'test/2'}

    client = test_client_factory(app)
    with client.websocket_connect('/') as websocket:
        data = websocket.receive_json()
        assert data == {'your_id': 'test'}
        websocket.send_json({'type': 'subscribe', 'topic': 'test/1', 'conn_id': 'test'})
        websocket.send_json({'type': 'subscribe', 'topic': 'test/2', 'conn_id': 'test'})
        websocket.send_json(
            {'type': 'unsubscribe', 'topic': 'test/1', 'conn_id': 'test'}
        )
