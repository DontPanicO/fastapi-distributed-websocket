__all__ = (
    'tag_client_message',
    'validate_incoming_message',
    'untag_broker_message',
    'Message',
)

import json
from typing import Any

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
__NULL_TOPIC_ALLOWED_TYPES = {
    'connect',
    'set_conn_id',
    'broadcast',
    'send_by_conn_id',
}
__REQUIRE_CONN_ID_TYPES = {'set_conn_id', 'send_by_conn_id'}


def is_valid_type_message(data: dict) -> bool:
    return data.get('type') in __VALID_TYPES


def is_valid_type_client_message(data: dict) -> bool:
    return data.get('type') in __VALID_TYPES - __SERVER_ONLY_TYPES


def tag_client_message(data: dict) -> Any:
    topic = data.get('topic', None)
    if topic is None:
        return update(data, **{'type': 'broadcast'})
    return data


def validate_incoming_message(data: dict) -> None:
    typ, topic, conn_id = (
        data.get('type'),
        data.get('topic'),
        data.get('conn_id'),
    )
    if not is_valid_type_client_message(data):
        raise ValueError(f'Invalid message type: {typ}')
    if topic is None and typ not in __NULL_TOPIC_ALLOWED_TYPES:
        raise ValueError(f'Invalid message type "{typ}" with no topic')
    if conn_id is None and typ in __REQUIRE_CONN_ID_TYPES:
        raise ValueError(f'Invalid message type "{typ}" with no conn_id')


def untag_broker_message(data: dict | str) -> tuple:
    if isinstance(data, (str, bytes)):
        data: dict = json.loads(data)
    return data.pop('type'), data.pop('topic'), data.pop('conn_id'), data


class Message:
    def __init__(
        self,
        *,
        data: Any,
        typ: str,
        topic: str | None = None,
        conn_id: str | list[str] | None = None,
    ) -> None:
        self.typ = typ
        self.topic = topic
        self.conn_id = conn_id
        self.data = data

    @classmethod
    def from_client_message(cls, *, data: dict) -> 'Message':
        return cls(
            data=data,
            typ=data.pop('type', None),
            topic=data.pop('topic', None),
            conn_id=data.pop('conn_id', None),
        )

    def __serialize__(self) -> dict[str, Any]:
        self.data['type'] = self.typ
        self.data['topic'] = self.topic
        self.data['conn_id'] = self.conn_id
        return self.data
