import asyncio
from abc import ABC, abstractmethod
from typing import Any, NoReturn
from collections.abc import Coroutine
from urllib.parse import urlparse

from aioredis import Redis
from aioredis.client import PubSub

from ._message import Message, untag_broker_message


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
    async def get_message(self, **kwargs) -> Coroutine[Any, Any, Message | None]:
        pass


class InMemoryBroker(BrokerInterface):
    def __init__(self) -> NoReturn:
        self._subscribers: set = set()
        self._messages: asyncio.Queue = asyncio.Queue()

    async def __aenter__(self) -> Coroutine[Any, Any, BrokerInterface]:
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

    async def get_message(self, **kwargs) -> Coroutine[Any, Any, Message | None]:
        message = await self._messages.get()
        if self.has_subscribers(message['channel'])
            typ, topic, data = untag_broker_message(message['data'])
            return Message(typ=typ, topic=topic, data=data)

    def has_subscribers(self, channel: str) -> bool:
        return channel in self._subscribers


class RedisBroker(BrokerInterface):
    def __init__(self, redis_url: str,) -> NoReturn:
        self._redis: Redis = Redis.from_url(redis_url)
        self._pubsub: PubSub = self._redis.pubsub()
    
    async def __aenter__(self) -> Coroutine[Any, Any, BrokerInterface]:
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> NoReturn:
        await self._pubsub.reset()
        await self._redis.close()

    async def subscribe(self, channel: str) -> Coroutine[Any, Any, NoReturn]:
        await self._pubsub.subscribe(channel)
    
    async def unsubscribe(self, channel: str) -> Coroutine[Any, Any, NoReturn]:
        await self._pubsub.unsubscribe(channel)
    
    async def publish(self, channel: str, message: Any) -> Coroutine[Any, Any, NoReturn]:
        await self._redis.publish(channel, message)
    
    async def get_message(self, **kwargs) -> Coroutine[Any, Any, Message | None]:
        message = await self._pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            typ, topic, data = untag_broker_message(message['data'])
            return Message(typ=typ, topic=topic, data=data)


def _create_inmemory_broker() -> InMemoryBroker:
    return InMemoryBroker()


def _create_redis_broker(
    redis_url: str,
) -> RedisBroker:
    return RedisBroker(redis_url)


def create_broker(broker_url: str, **kwargs) -> BrokerInterface:
    url = urlparse(broker_url)
    if url.scheme == 'redis':
        return _create_redis_broker(url.netloc)
    elif url.scheme == 'memory':
        return _create_inmemory_broker()
    raise ValueError(f'Unknown broker url: {broker_url}')
