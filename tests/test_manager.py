import asyncio
import signal
from collections.abc import Callable

import pytest
from starlette import status
from starlette.testclient import TestClient
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from distributed_websocket import Connection, Message, WebSocketManager


def test_manager_01(
    test_client_factory: Callable[
        [Callable[[Scope, Receive, Send], None]], TestClient
    ]
):
    manager = WebSocketManager('test', 'memory://')

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive, send)
        connection = await manager.new_connection(websocket, 'conn1')
        connection.topics.add('tests/1')
        manager.send(
            Message(
                data={'msg': 'hello'},
                typ='send',
                topic='tests/1',
            )
        )

    test_client = test_client_factory(app)
    with test_client.websocket_connect('/') as websocket:
        msg = websocket.receive_json()
        assert msg == {'msg': 'hello'}

    for t in manager._send_tasks:
        if not t.done():
            t.cancel()


def test_manager_02(
    test_client_factory: Callable[
        [Callable[[Scope, Receive, Send], None]], TestClient
    ]
):
    manager = WebSocketManager('test', 'memory://')

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive, send)
        conn_id = websocket.query_params['myid'] or 'connx'
        connection = await manager.new_connection(websocket, conn_id)
        connection.topics.add('tests/1')
        manager.send(
            Message(
                data={'msg': 'hello'},
                typ='send',
                topic='tests/1',
            )
        )

    test_client1 = test_client_factory(app)
    test_client2 = test_client_factory(app)
    with test_client1.websocket_connect(
        '/?myid=conn1'
    ) as w1, test_client2.websocket_connect('/?myid=conn2') as w2:
        msg1 = w1.receive_json()
        msg2 = w2.receive_json()
        assert msg1 == msg2 == {'msg': 'hello'}

    for t in manager._send_tasks:
        if not t.done():
            t.cancel()


@pytest.mark.asyncio
async def test_manager_broadcast(
    test_client_factory: Callable[
        [Callable[[Scope, Receive, Send], None]], TestClient
    ],
):
    manager = WebSocketManager('test', 'memory://')
    await manager.startup()

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive, send)
        conn_id = websocket.query_params['myid'] or 'connx'
        connection = await manager.new_connection(websocket, conn_id)
        connection.topics.add('tests/1')
        async for m in connection:
            await manager.receive(connection, m)
        manager.remove_connection(connection)

    test_client1 = test_client_factory(app)
    test_client2 = test_client_factory(app)
    with test_client1.websocket_connect(
        '/?myid=conn1'
    ) as w1, test_client2.websocket_connect('/?myid=conn2') as w2:
        w1.send_json(
            {
                'type': 'broadcast',
                'topic': 'tests/1',
                'conn_id': 'conn1',
                'msg': 'hello',
            }
        )
        await asyncio.sleep(0.01)
        msg1 = w1.receive_json()
        msg2 = w2.receive_json()
        assert msg1 == msg2 == {'msg': 'hello'}

    await manager.shutdown()


@pytest.mark.asyncio
async def test_manager_send_01(
    test_client_factory: Callable[
        [Callable[[Scope, Receive, Send], None]], TestClient
    ],
):
    manager = WebSocketManager('test', 'memory://')
    await manager.startup()

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive, send)
        conn_id = websocket.query_params['myid'] or 'connx'
        connection = await manager.new_connection(websocket, conn_id)
        connection.topics.add('tests/1')
        async for m in connection:
            await manager.receive(connection, m)
        manager.remove_connection(connection)

    test_client1 = test_client_factory(app)
    test_client2 = test_client_factory(app)
    with test_client1.websocket_connect(
        '/?myid=conn1'
    ) as w1, test_client2.websocket_connect('/?myid=conn2') as w2:
        w1.send_json(
            {
                'type': 'send',
                'topic': 'tests/1',
                'conn_id': 'conn1',
                'msg': 'hello',
            }
        )
        await asyncio.sleep(0.01)
        msg1 = w1.receive_json()
        msg2 = w2.receive_json()
        assert msg1 == msg2 == {'msg': 'hello'}

    await manager.shutdown()


@pytest.mark.asyncio
async def test_manager_send_02(
    test_client_factory: Callable[
        [Callable[[Scope, Receive, Send], None]], TestClient
    ],
):
    manager = WebSocketManager('test', 'memory://')
    await manager.startup()

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive, send)
        conn_id = websocket.query_params['myid'] or 'connx'
        connection = await manager.new_connection(websocket, conn_id)
        connection.topics.add('tests/1')
        async for m in connection:
            await manager.receive(connection, m)
        manager.remove_connection(connection)

    test_client1 = test_client_factory(app)
    test_client2 = test_client_factory(app)
    with test_client1.websocket_connect(
        '/?myid=conn1'
    ) as w1, test_client2.websocket_connect('/?myid=conn2') as w2:
        w1.send_json(
            {
                'type': 'send',
                'topic': 'tests/2',
                'conn_id': 'conn1',
                'msg': 'hello',
            }
        )
        await asyncio.sleep(0.01)
        msg1 = msg2 = None

        def handle_alarm(sig, frame):
            raise TimeoutError

        signal.signal(signal.SIGALRM, handle_alarm)

        def get_msg1():
            nonlocal msg1
            signal.alarm(1)
            msg1 = w1.receive_json()

        def get_msg2():
            nonlocal msg2
            signal.alarm(1)
            msg2 = w2.receive_json()

        with pytest.raises(TimeoutError):
            get_msg1()
            get_msg2()

        assert msg1 == msg2 == None

    await manager.shutdown()


@pytest.mark.asyncio
async def test_manager_send_by_conn_id_01(
    test_client_factory: Callable[
        [Callable[[Scope, Receive, Send], None]], TestClient
    ],
):
    manager = WebSocketManager('test', 'memory://')
    await manager.startup()

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive, send)
        conn_id = websocket.query_params['myid'] or 'connx'
        connection = await manager.new_connection(websocket, conn_id)
        connection.topics.add('tests/1')
        async for m in connection:
            await manager.receive(connection, m)
        manager.remove_connection(connection)

    test_client1 = test_client_factory(app)
    test_client2 = test_client_factory(app)
    with test_client1.websocket_connect(
        '/?myid=conn1'
    ) as w1, test_client2.websocket_connect('/?myid=conn2') as w2:
        w1.send_json(
            {
                'type': 'send_by_conn_id',
                'topic': None,
                'conn_id': 'conn3',
                'msg': 'hello',
            }
        )
        await asyncio.sleep(0.01)
        msg1 = msg2 = None

        def handle_alarm(sig, frame):
            raise TimeoutError

        signal.signal(signal.SIGALRM, handle_alarm)

        def get_msg1():
            nonlocal msg1
            signal.alarm(1)
            msg1 = w1.receive_json()

        def get_msg2():
            nonlocal msg2
            signal.alarm(1)
            msg2 = w2.receive_json()

        with pytest.raises(TimeoutError):
            get_msg1()
            get_msg2()
        assert msg1 == msg2 == None

    await manager.shutdown()


@pytest.mark.asyncio
async def test_manager_send_by_conn_id_02(
    test_client_factory: Callable[
        [Callable[[Scope, Receive, Send], None]], TestClient
    ],
):
    manager = WebSocketManager('test', 'memory://')
    await manager.startup()

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive, send)
        conn_id = websocket.query_params['myid'] or 'connx'
        connection = await manager.new_connection(websocket, conn_id)
        connection.topics.add('tests/1')
        async for m in connection:
            await manager.receive(connection, m)
        manager.remove_connection(connection)

    test_client1 = test_client_factory(app)
    test_client2 = test_client_factory(app)
    with test_client1.websocket_connect(
        '/?myid=conn1'
    ) as w1, test_client2.websocket_connect('/?myid=conn2') as w2:
        w1.send_json(
            {
                'type': 'send_by_conn_id',
                'topic': None,
                'conn_id': 'conn2',
                'msg': 'hello',
            }
        )
        await asyncio.sleep(0.01)
        msg1 = None

        def handle_alarm(sig, frame):
            raise TimeoutError

        signal.signal(signal.SIGALRM, handle_alarm)

        def get_msg1():
            nonlocal msg1
            signal.alarm(1)
            msg1 = w1.receive_json()

        with pytest.raises(TimeoutError):
            get_msg1()
        msg2 = w2.receive_json()
        assert msg1 is None
        assert msg2 == {'msg': 'hello'}

    await manager.shutdown()
