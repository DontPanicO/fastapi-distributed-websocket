import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Any, NoReturn
from collections.abc import Coroutine
from urllib.parse import urlparse

from aioredis import Redis
from aioredis.client import PubSub


class BrokerInterface(ABC):
    @abstractmethod
    async def subscribe(self, channel: str) -> Coroutine[Any, Any, NoReturn]:
        pass

    @abstractmethod
    async def unsubscribe(self, channel: str) -> Coroutine[Any, Any, NoReturn]:
        pass

    @abstractmethod
    async def publish(
        self, channel: str, message: Any
    ) -> Coroutine[Any, Any, NoReturn]:
        pass

    @abstractmethod
    async def get_message(self, **kwargs) -> Coroutine[Any, Any, dict | None]:
        pass


class InMemoryBroker(BrokerInterface):
    def __init__(self) -> NoReturn:
        self._subscribers: set = set()
        self._messages: asyncio.Queue = asyncio.Queue()

    async def __aenter__(self) -> Coroutine[Any, Any, 'InMemoryBroker']:
        return self

    async def __aexit__(
        self, exc_type, exc_val, exc_tb
    ) -> Coroutine[Any, Any, NoReturn]:
        pass

    async def subscribe(self, channel: str) -> Coroutine[Any, Any, NoReturn]:
        self._subscribers.add(channel)

    async def unsubscribe(self, channel: str) -> Coroutine[Any, Any, NoReturn]:
        self._subscribers.remove(channel)

    async def publish(
        self, channel: str, message: Any
    ) -> Coroutine[Any, Any, NoReturn]:
        await self._messages.put({'channel': channel, 'data': message})

    async def get_message(self, **kwargs) -> Coroutine[Any, Any, dict | None]:
        message = await self._messages.get()
        if message['channel'] in self._subscribers:
            return message

    def has_subscribers(self, channel: str) -> bool:
        return channel in self._subscribers


class RedisBroker(PubSub, BrokerInterface):

    '''
    This class does not override any of `aioredis.client.PubSub` methods,
    while also inheriting from `BrokerInterface` to have logical cohesion
    with broker objects
    '''


def _create_redis_broker(
    redis_url: str,
    shard_hint: str | None = None,
    ignore_subscribe_messages: bool = False,
) -> RedisBroker:
    redis = Redis.from_url(redis_url)
    return RedisBroker(redis.connection_pool, shard_hint, ignore_subscribe_messages)


def create_broker(broker_url: str, **kwargs) -> BrokerInterface:
    url = urlparse(broker_url)
    if url.scheme == 'redis':
        return _create_redis_broker(url.netloc, **kwargs)
    elif url.scheme == 'memory':
        return InMemoryBroker()
    raise ValueError(f'Unknown broker url: {broker_url}')
