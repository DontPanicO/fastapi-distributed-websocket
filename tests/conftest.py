import asyncio
from collections.abc import AsyncGenerator, Generator

import aiohttp
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from .app import app


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app_obj() -> FastAPI:
    return app


@pytest.fixture
async def session(app_obj: FastAPI) -> AsyncGenerator[aiohttp.ClientSession, None]:
    async with LifespanManager(app_obj):
        async with aiohttp.ClientSession(
            base_url='http://testserver', headers={'Content-Type': 'application/json'}
        ) as session:
            yield session
