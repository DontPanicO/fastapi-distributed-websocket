import inspect
from typing import Any
from collections.abc import Coroutine, Callable
from functools import wraps


async def _await_maybe(result: Any) -> Coroutine[Any, Any, Any]:
    if inspect.isawaitable(result):
        return await result
    return result


def handle(exc: BaseException, handler: Callable[..., Any]) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except exc as e:
                return handler(e)

        return wrapper

    return decorator


def ahandle(
    exc: BaseException, handler: Callable[..., Coroutine[Any, Any, Any]]
) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await _await_maybe(func(*args, **kwargs))
            except exc as e:
                return await handler(e)

        return wrapper

    return decorator
