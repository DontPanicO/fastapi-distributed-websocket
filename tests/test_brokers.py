import asyncio

import pytest
from distributed_websocket._broker import create_broker
from distributed_websocket._message import tag_client_message


@pytest.mark.asyncio
async def test_inmemory_broker() -> None:
    async with create_broker('memory://') as broker:
        await broker.subscribe('test')
        await broker.publish('test', tag_client_message({'msg': 'hello'}))
        message = await broker.get_message()
        assert message.data == {'msg': 'hello'}


@pytest.mark.asyncio
async def test_redis_broker() -> None:
    async with create_broker('redis://redis') as broker:
        await broker.subscribe('test')
        await broker.publish('test', tag_client_message({'msg': 'hello'}))
        i = 0
        message = await broker.get_message()
        while message is None:
            await asyncio.sleep(0.01)
            message = await broker.get_message()
            if i > 2:
                break
            i += 1
        assert i < 2
        print(message, i)
        assert message.data == {'msg': 'hello'}
