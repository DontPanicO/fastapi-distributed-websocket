import asyncio

import pytest
from aiohttp.test_utils import TestClient


@pytest.mark.asyncio
async def test_ws_endpoint(
    client: TestClient, event_loop: asyncio.AbstractEventLoop
) -> None:
    async with client.ws_connect(path='/ws/') as ws:
        await ws.send_json({'name': 'test'})
        response = await ws.receive_json()
        assert response == {'name': 'test'}
