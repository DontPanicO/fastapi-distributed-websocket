__all__ = ['BrokerT']

import typing
import aioredis

from ._inmemory_broker import InMemoryBroker


BrokerT = typing.Union[aioredis.client.PubSub, InMemoryBroker]
