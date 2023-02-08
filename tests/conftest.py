import asyncio
import functools
from collections.abc import AsyncGenerator, Generator

import anyio
import pytest
from starlette.testclient import TestClient


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client_factory(anyio_backend_options):
    # anyio_backend_name defined by:
    # https://anyio.readthedocs.io/en/stable/testing.html#specifying-the-backends-to-run-on
    return functools.partial(
        TestClient,
        backend='asyncio',
        backend_options=anyio_backend_options,
    )
