import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from fastapi import FastAPI
from fastapi.testclient import TestClient

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
def client(app_obj: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app_obj) as client:
        yield client
