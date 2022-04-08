__all__ = ['BrokerT']

import typing
import aioredis

from ._broker import BrokerInterface


# TODO: Declare type using typing
BrokerT = BrokerInterface
