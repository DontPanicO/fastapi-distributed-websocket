__all__ = ('send_error_message',)

from ._exceptions import WebSocketException


async def send_error_message(exc: WebSocketException) -> None:
    await exc.connection.send_json({'error': exc.message})
