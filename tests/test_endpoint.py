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
    auth_rsp = await session.post(
        '/token', data={'username': 'johndoe', 'password': 'secret'}
    )
    auth_token = auth_rsp.json()['access_token']
    session.headers.update({'Authorization': f'Bearer {auth_token}'})
