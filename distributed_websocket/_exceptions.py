class WebSocketException(BaseException):
    '''
    Base class for all WebSocket exceptions, other than
    those provided by FastAPI.
    '''
    ...


class InvalidSubscription(ValueError):
    '''
    Raised when a subscription pattern is invalid.
    '''
    ...


class InvalidSubscriptionMessage(ValueError):
    '''
    Raised when a subscription message is invalid.
    Differs from `InvalidSubscription` in that it also
    checks the validity of the message type.
    '''
    ...
