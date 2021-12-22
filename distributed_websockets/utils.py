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


def load_message_data(msg: dict) -> Optional[Any]:
    if is_valid_json(msg['data']):
        return json.loads(msg['data'])


def dump_message_data(data: Any) -> Optional[str]:
    return json.dumps(data)
