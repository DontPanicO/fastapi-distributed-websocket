import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import aiohttp
from aiohttp.test_utils import TestServer, TestClient
from fastapi import FastAPI

from .app import app


# @pytest.fixture(scope='session')
# def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
#     # loop = asyncio.get_event_loop_policy().new_event_loop()
#     loop = asyncio.get_running_loop()
#     yield loop
#     loop.close()


@pytest.fixture
def app_obj() -> FastAPI:
    return app


@pytest.fixture
async def client(app_obj: FastAPI) -> Generator:
    async with TestServer(app_obj) as server:
        async with TestClient(server) as client:
            yield client
