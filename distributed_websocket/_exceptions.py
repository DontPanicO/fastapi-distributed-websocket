__all__ = (
    'WebSocketException',
    'InvalidSubscription',
    'InvalidSubscriptionMessage',
)

from ._connection import Connection


class WebSocketException(BaseException):
    '''
    Base class for all WebSocket exceptions, other than
    those provided by FastAPI.
    Its main purpose is to provide a message to the client,
    keeping a reference to the connection object that the
    exception handler can use.
    '''

    def __init__(self, message: str, *, connection: Connection) -> None:
        self.message = message
        self.connection = connection
        super().__init__(message)


class InvalidSubscription(WebSocketException):
    '''
    Raised when a subscription pattern is invalid.
    '''

    ...


class InvalidSubscriptionMessage(WebSocketException):
    '''
    Raised when a subscription message is invalid.
    Differs from `InvalidSubscription` in that it also
    checks the validity of the message type.
    '''

    ...
