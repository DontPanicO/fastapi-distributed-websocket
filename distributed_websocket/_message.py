import json
from typing import Any, NoReturn

from .utils import update


__VALID_TYPES = {
    'connect',
    'set_conn_id',
    'subscribe',
    'unsubscribe',
    'broadcast',
    'send',
    'send_by_conn_id',
}
__SERVER_ONLY_TYPES = {'set_conn_id'}
__CLIENT_ONLY_TYPES = {'connect'}


def is_valid_type_message(data: dict) -> bool:
    return data.get('type') in __VALID_TYPES


def is_valid_type_client_message(data: dict) -> bool:
    return data.get('type') in __VALID_TYPES - __SERVER_ONLY_TYPES


def tag_client_message(data: dict) -> Any:
    topic = data.get('topic', None)
    if topic is None:
        return update(data, **{'type': 'broadcast'})
    return data


def untag_broker_message(data: dict | str) -> tuple:
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
