import asyncio

import pytest
from distributed_websocket import InMemoryBroker
from distributed_websocket._message import tag_client_message


@pytest.mark.asyncio
async def test_broker() -> None:
    async with InMemoryBroker() as broker:
        await broker.subscribe('test')
        await broker.publish('test', tag_client_message({'msg': 'hello'}))
        message = await broker.get_message()
        assert message.data == {'msg': 'hello'}
