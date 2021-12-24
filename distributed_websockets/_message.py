import json
from typing import Optional, Any, NoReturn

from .utils import is_valid_json


class Message:
    def __init__(
        self,
        topic: str,
        data: Any,
        type: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> NoReturn:
        self.topic: str = topic
        self.data: Any = data
        self.type: Optional[str] = type
        self.pattern: Optional[None] = pattern

    @property
    def __dict__(self) -> dict:
        return {
            'topic': self.topic,
            'data': self.data,
            'type': self.type,
            'pattern': self.pattern,
        }

    def __serialize__(self) -> str:
        assert is_valid_json(self.data), 'Message data must be valid JSON'
        return json.dumps(self.data)

    @classmethod
    def deserialize(cls, data: dict) -> 'Message':
        return cls(data['topic'], data['data'])
