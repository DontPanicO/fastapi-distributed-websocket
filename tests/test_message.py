import pytest

from distributed_websocket._message import Message, untag_broker_message


def test_message_01():
    m = Message(
        data={'msg': 'hello'},
        typ='send',
        topic='test',
        conn_id='test',
    )
    assert m.data == {'msg': 'hello'}
    data = m.__serialize__()
    assert data == {
        'msg': 'hello',
        'type': 'send',
        'topic': 'test',
        'conn_id': 'test',
    }


def test_message_02():
    m = Message.from_client_message(
        data={'msg': 'hello', 'type': 'send', 'topic': 'test', 'conn_id': 'test'}
    )
    assert m.data == {'msg': 'hello'}
    assert m.typ == 'send'
    assert m.topic == 'test'
    assert m.conn_id == 'test'


def test_untag_broker_message_01():
    typ, topic, conn_id, data = untag_broker_message(
        '{"msg": "hello", "type": "send", "topic": "test", "conn_id": "test"}'
    )
    assert typ == 'send'
    assert topic == 'test'
    assert conn_id == 'test'
    assert data == {'msg': 'hello'}
