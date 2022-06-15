__all__ = ['WebSocketProxy']

import asyncio
from typing import Any, NoReturn
from collections.abc import Coroutine

import websockets
from fastapi import WebSocket, WebSocketDisconnect


async def _forward(
    client: WebSocket, target: websockets.WebSocketClientProtocol
) -> Coroutine[Any, Any, NoReturn]:
    async for message in client.iter_text():
        await target.send(message)


async def _reverse(
    client: WebSocket, target: websockets.WebSocketClientProtocol
) -> Coroutine[Any, Any, NoReturn]:
    async for message in target:
        await client.send_text(message)


class WebSocketProxy:
    def __init__(self, client: WebSocket, server_endpoint: str) -> NoReturn:
        self._client = client
        self._server_endpoint = server_endpoint
        self._tasks: set[asyncio.Task] = set()

    async def __call__(self) -> Coroutine[Any, Any, NoReturn]:
        async with websockets.connect(self._server_endpoint) as server:
            self._tasks.add(asyncio.create_task(_forward(self._client, server)))
            self._tasks.add(asyncio.create_task(_reverse(self._client, server)))
