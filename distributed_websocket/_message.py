import json
from typing import Optional, Any, NoReturn

from .utils import is_valid_json, update


def tag_client_message(data: dict, topic: str | None = None) -> Any:
    if not topic:
        return update(data, **{'type': 'broadcast', 'topic': None})
    return update(data, **{'type': 'publish', 'topic': topic})


def untag_broker_message(data: dict | str) -> Any:
    if isinstance(data, str):
        data: dict = json.loads(data)
    return data.pop('type'), data.pop('topic'), data
