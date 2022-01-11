import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import aiohttp
from fastapi import FastAPI

from .app import app


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    async with aiohttp.ClientSession('http://testapp:8000') as session:
        yield session
