import asyncio

import pytest
import httpx
from fastapi import FastAPI

from .app import app


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def app_obj():
    return app


# @pytest.fixture(scope='session')
# def client(app_obj: FastAPI):
