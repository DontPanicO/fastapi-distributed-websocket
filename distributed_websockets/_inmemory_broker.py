import asyncio
from typing import Optional, Any, NoReturn


class InMemoryBroker:
    def __init__(self) -> NoReturn:
        self._subscribers: set = set()
        self._messages: asyncio.Queue = asyncio.Queue()
    
    async def subscribe(self, topic: str) -> NoReturn:
        self._subscribers.add(topic)
    
    async def unsubscribe(self, topic: str) -> NoReturn:
        self._subscribers.remove(topic)
    
    async def publish(self, topic: str, message: Any) -> NoReturn:
        await self._messages.put({'channel': topic, 'data': message})
    
    async def get_message(self) -> Optional[dict]:
        message = await self._messages.get()
        if message['channel'] in self._subscribers:
            return message
    
    def has_subscribers(self, topic: str) -> bool:
        return topic in self._subscribers
