__all__ = ('BrokerInterface', 'create_broker')

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlparse

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from ._message import Message, untag_broker_message


class BrokerInterface(ABC):
    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def subscribe(self, channel: str) -> None:
        ...

    @abstractmethod
    async def unsubscribe(self, channel: str) -> None:
        ...

    @abstractmethod
    async def publish(self, channel: str, message: Any) -> None:
        ...

    @abstractmethod
    async def get_message(self, **kwargs) -> Message | None:
        ...


class InMemoryBroker(BrokerInterface):
    def __init__(self) -> None:
        self._subscribers: set = set()
        self._messages: asyncio.Queue = asyncio.Queue()

    async def __aenter__(self) -> BrokerInterface:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def subscribe(self, channel: str) -> None:
        self._subscribers.add(channel)

    async def unsubscribe(self, channel: str) -> None:
        self._subscribers.remove(channel)

    async def publish(self, channel: str, message: Any) -> None:
        await self._messages.put({'channel': channel, 'data': message})

    async def get_message(self, **kwargs) -> Message | None:
        message = await self._messages.get()
        if self.has_subscribers(message['channel']):
            typ, topic, conn_id, data = untag_broker_message(message['data'])
            return Message(data=data, typ=typ, topic=topic, conn_id=conn_id)

    def has_subscribers(self, channel: str) -> bool:
        return channel in self._subscribers


class RedisBroker(BrokerInterface):
    def __init__(
        self,
        redis_url: str,
    ) -> None:
        self._redis: Redis = Redis.from_url(redis_url)
        self._pubsub: PubSub = self._redis.pubsub()

    async def __aenter__(self) -> BrokerInterface:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        await self._pubsub.reset()
        await self._redis.close()

    async def subscribe(self, channel: str) -> None:
        await self._pubsub.subscribe(channel)

    async def unsubscribe(self, channel: str) -> None:
        await self._pubsub.unsubscribe(channel)

    async def publish(self, channel: str, message: Any) -> None:
        if isinstance(message, dict):
            message = json.dumps(message)
        await self._redis.publish(channel, message)

    async def get_message(self, **kwargs) -> Message | None:
        message = await self._pubsub.get_message(
            ignore_subscribe_messages=True
        )
        if message:
            typ, topic, conn_id, data = untag_broker_message(message['data'])
            return Message(data=data, typ=typ, topic=topic, conn_id=conn_id)


def _create_inmemory_broker() -> InMemoryBroker:
    return InMemoryBroker()


def _create_redis_broker(
    redis_url: str,
) -> RedisBroker:
    return RedisBroker(redis_url)


def create_broker(broker_url: str, **kwargs) -> BrokerInterface:
    url = urlparse(broker_url)
    if url.scheme == 'redis':
        return _create_redis_broker(broker_url)
    elif url.scheme == 'memory':
        return _create_inmemory_broker()
    raise ValueError(f'Unknown broker url: {broker_url}')
