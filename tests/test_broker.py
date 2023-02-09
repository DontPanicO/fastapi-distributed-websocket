import pytest

from distributed_websocket._broker import create_broker
from distributed_websocket._message import tag_client_message


@pytest.mark.asyncio
async def test_inmemory_broker() -> None:
    async with create_broker('memory://') as broker:
        await broker.subscribe('test')
        await broker.publish(
            'test',
            {'type': 'broadcast', 'topic': None, 'conn_id': None, 'msg': 'hello'},
        )
        message = await broker.get_message()
        assert message.data == {'msg': 'hello'}
