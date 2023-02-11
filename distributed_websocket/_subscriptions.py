__all__ = (
    'is_subscription_message',
    'subscribe',
    'unsubscribe',
    'handle_subscription_message',
)

from ._connection import Connection
from ._exceptions import InvalidSubscriptionMessage
from ._message import Message


def is_subscription_message(message: Message) -> bool:
    return message.typ == 'subscribe' or message.typ == 'unsubscribe'


def _is_valid_subscription(topic: str) -> bool:
    return topic is not None and len(topic) and '/' in topic


def _check_subscription_message(message: Message) -> bool:
    return is_subscription_message(message) and _is_valid_subscription(
        message.topic
    )


def subscribe(connection: Connection, message: Message) -> None:
    if not _check_subscription_message(message):
        raise InvalidSubscriptionMessage(
            f'"{message}" is not a valid subscription message',
            connection=connection,
        )
    connection.topics.add(message.topic)


def unsubscribe(connection: Connection, message: Message) -> None:
    if not _check_subscription_message(message):
        raise InvalidSubscriptionMessage(
            f'"{message}" is not a valid subscription message',
            connection=connection,
        )
    if message.topic in connection.topics:
        connection.topics.remove(message.topic)


def handle_subscription_message(
    connection: Connection, message: Message
) -> None:
    if message.typ == 'subscribe':
        subscribe(connection, message)
    else:
        unsubscribe(connection, message)
