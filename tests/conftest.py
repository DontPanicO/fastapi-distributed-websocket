import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
import aiohttp
from fastapi import FastAPI

from .app import app


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    async with aiohttp.ClientSession() as session:
        yield session
