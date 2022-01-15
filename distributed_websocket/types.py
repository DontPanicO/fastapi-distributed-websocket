__all__ = ['BrokerT']

import typing
import aioredis

from ._inmemory_broker import InMemoryBroker


BrokerT = aioredis.client.PubSub | InMemoryBroker | typing.Any
