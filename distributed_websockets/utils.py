import inspect
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


def is_valid_broker(obj: Any) -> bool:
    """
    Helper utils to check if an object can
    be used as a broker in `WebSocketManager`.
    Exposed to developers who need to implement a
    custom broker.
    """
    return (
        (hasattr(obj, 'subscribe') and inspect.iscoroutinefunction(obj.subscribe))
        and (hasattr(obj, 'unsubscribe') and inspect.iscoroutinefunction(obj.unsubscribe))
        and (hasattr(obj, 'publish') and inspect.iscoroutinefunction(obj.publish))
        and (hasattr(obj, 'get_message') and inspect.iscoroutinefunction(obj.get_message))
    )
