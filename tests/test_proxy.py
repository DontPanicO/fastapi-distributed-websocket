import asyncio
from collections.abc import Coroutine
import typing

import aiohttp
import pytest



@pytest.mark.asyncio
async def test_proxy_endpoint(
    session: aiohttp.ClientSession, event_loop: asyncio.AbstractEventLoop
) -> Coroutine[None, None, None]:
    async with session.ws_connect('http://test_api_gateway:8000/ws') as ws:
        await ws.send_json({'message': 'hello'})
        message = await ws.receive_json()
        assert message == {'message': 'hello'}
