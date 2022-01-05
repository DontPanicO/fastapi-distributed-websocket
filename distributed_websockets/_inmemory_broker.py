import asyncio
from typing import Optional, Any, NoReturn
from collections.abc import Coroutine


class InMemoryBroker:
    def __init__(self) -> NoReturn:
        self._subscribers: set = set()
        self._messages: asyncio.Queue = asyncio.Queue()

    async def subscribe(self, channel: str) -> Coroutine[Any, Any, NoReturn]:
        self._subscribers.add(channel)

    async def unsubscribe(self, channel: str) -> Coroutine[Any, Any, NoReturn]:
        self._subscribers.remove(channel)

    async def publish(
        self, channel: str, message: Any
    ) -> Coroutine[Any, Any, NoReturn]:
        await self._messages.put({'channel': channel, 'data': message})

    async def get_message(self, **kwargs) -> Coroutine[Any, Any, Optional[dict]]:
        message = await self._messages.get()
        if message['channel'] in self._subscribers:
            return message

    def has_subscribers(self, channel: str) -> bool:
        return channel in self._subscribers
