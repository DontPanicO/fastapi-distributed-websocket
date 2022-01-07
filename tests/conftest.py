import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import websockets
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


# @pytest.fixture
# async def session(app_obj: FastAPI):
