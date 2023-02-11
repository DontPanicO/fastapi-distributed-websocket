__all__ = ('Connection',)

from collections.abc import AsyncGenerator, AsyncIterator, Coroutine
from typing import Any, Callable

from fastapi import WebSocket, WebSocketDisconnect, status

from ._message import Message, validate_incoming_message


class Connection:
    def __init__(
        self, websocket: WebSocket, conn_id: str, topic: str | None = None
    ) -> None:
        self.websocket: WebSocket = websocket
        self.id: str = conn_id
        self.topics: set = {topic} if topic else set()
        self._message_generator: AsyncGenerator[None, Message] | None = None
        self.accept: Callable[
            [str | None], Coroutine[Any, Any, None]
        ] = websocket.accept
        self.receive_json: Callable[
            [str], Coroutine[Any, Any, Any]
        ] = websocket.receive_json
        self.send_json: Callable[
            [Any, str], Coroutine[Any, Any, None]
        ] = websocket.send_json
        self.iter_json: Callable[[], AsyncIterator] = websocket.iter_json

    def __aiter__(self) -> AsyncIterator:
        return self

    async def __anext__(self) -> Message:
        try:
            data = await self.receive_json()
            validate_incoming_message(data)
            return Message.from_client_message(data=data)
        except ValueError as exc:
            await self.send_json({'error': f'{exc}'})
            return None
        except WebSocketDisconnect:
            raise StopAsyncIteration from None

    async def close(self, code: int = status.WS_1000_NORMAL_CLOSURE) -> None:
        await self.websocket.close(code)
