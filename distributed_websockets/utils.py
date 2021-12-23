from typing import Optional, Any, NoReturn

import asyncio
import json


def clear_task(task: asyncio.Task) -> NoReturn:
    if task.done():
        task.result()
    else:
        task.cancel()


def is_valid_json(data: Any) -> bool:
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


def serialize(obj: Any) -> Any:
    assert hasattr(obj, '__serialize__'), 'Object must have __serialize__ method'
    return obj.__serialize__()
