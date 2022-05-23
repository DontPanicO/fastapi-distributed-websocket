import json
from typing import Any, NoReturn

from .utils import update


def tag_client_message(data: dict, topic: str | None = None) -> Any:
    if not topic:
        return update(data, **{'type': 'broadcast', 'topic': None})
    return update(data, **{'type': 'send', 'topic': topic})


def untag_broker_message(data: dict | str) -> Any:
    if isinstance(data, (str, bytes)):
        data: dict = json.loads(data)
    return data.pop('type'), data.pop('topic'), data


class Message:
    def __init__(self, *, data: Any, typ: str, topic: str | None = None) -> NoReturn:
        self.typ = typ
        self.topic = topic
        self.data = data
    
    @classmethod
    def from_client_message(cls, *, data: Any) -> 'Message':
        return cls(data=data, typ=data['type'], topic=data['topic'])
    
    def __serialize__(self) -> dict[str, Any]:
        self.data['type'] = self.typ
        self.data['topic'] = self.topic
        return self.data