from typing import Any
from collections.abc import Coroutine

from ._connection import Connection
from ._exceptions import WebSocketException


async def send_error_message(exc: WebSocketException) -> Coroutine[Any, Any, None]:
    await exc.connection.send_json({'error': exc.message})
