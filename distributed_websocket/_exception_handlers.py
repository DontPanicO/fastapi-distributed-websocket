from typing import Any, NoReturn
from collections.abc import Coroutine

from ._connection import Connection


async def send_error_message(
    connection: Connection, message: str
) -> Coroutine[Any, Any, NoReturn]:
    await connection.send_json({'error': message})
