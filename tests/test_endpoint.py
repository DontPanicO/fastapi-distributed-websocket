import asyncio
from collections.abc import Coroutine
import typing

import aiohttp
import pytest


@pytest.mark.asyncio
async def test_endpoint(
    session: aiohttp.ClientSession, event_loop: asyncio.AbstractEventLoop
) -> Coroutine[None, None, typing.NoReturn]:
    async with session.ws_connect('/ws/broadcast/myid') as ws:
        await ws.send_json({'message': 'hello'})
        message = await ws.receive_json()
        assert message == {'message': 'hello'}


@pytest.mark.asyncio
async def test_authenticated_endpoint(
    session: aiohttp.ClientSession, event_loop: asyncio.AbstractEventLoop
) -> Coroutine[None, None, typing.NoReturn]:
    raw_rsp = await session.post(
        '/token', json={'username': 'johndoe', 'password': 'secret'}
    )
    rsp = await raw_rsp.json()
    assert 'access_token' in rsp
    session.headers.update({'Authorization': f'Bearer {rsp["access_token"]}'})
