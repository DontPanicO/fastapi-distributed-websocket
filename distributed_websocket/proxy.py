__all__ = ('WebSocketProxy',)

import asyncio

import websockets
from fastapi import WebSocket


async def _forward(
    client: WebSocket, target: websockets.WebSocketClientProtocol
) -> None:
    async for message in client.iter_text():
        await target.send(message)


async def _reverse(
    client: WebSocket, target: websockets.WebSocketClientProtocol
) -> None:
    async for message in target:
        await client.send_text(message)


class WebSocketProxy:
    def __init__(self, client: WebSocket, server_endpoint: str) -> None:
        self._client = client
        self._server_endpoint = server_endpoint
        self._forward_task: asyncio.Task | None = None
        self._reverse_task: asyncio.Task | None = None

    async def __call__(self) -> None:
        async with websockets.connect(self._server_endpoint) as target:
            self._forward_task = asyncio.create_task(
                _forward(self._client, target)
            )
            self._reverse_task = asyncio.create_task(
                _reverse(self._client, target)
            )
            await asyncio.gather(self._forward_task, self._reverse_task)
