from typing import Any, NoReturn

from ._connection import Connection
from ._message import Message


def is_subscription_message(message: Message) -> bool:
    return message.typ == "subscribe" or message.typ == "unsubscribe"


def _is_valid_subscription(topic: str) -> bool:
    return topic is not None and len(topic) and "/" in topic


def _check_subscription_message(message: Message) -> bool:
    return is_subscription_message(message) and _is_valid_subscription(message.topic)


def subscribe(connection: Connection, message: Message) -> NoReturn:
    assert _check_subscription_message(
        message
    ), f"Message {message} is not valid for sub/unsub"
    connection.topics.add(message.topic)


def unsubscribe(connection: Connection, message: Message) -> NoReturn:
    assert _check_subscription_message(
        message
    ), f"Message {message} is not valid for sub/unsub"
    if topic in connection.topics:
        connection.topics.remove(message.topic)


def handle_subscription_message(connection: Connection, message: Message) -> NoReturn:
    if message.typ == "subscribe":
        subscribe(connection, message)
    else:
        unsubscribe(connection, message)
