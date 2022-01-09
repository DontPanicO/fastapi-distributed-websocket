import asyncio

import pytest
from distributed_websocket import InMemoryBroker


@pytest.mark.asyncio
async def test_broker():
    async with InMemoryBroker() as broker:
        await broker.subscribe('test')
        await broker.publish('test', 'hello')
        message = await broker.get_message()
        assert message['channel'] == 'test'
        assert message['data'] == 'hello'
