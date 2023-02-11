__all__ = ('handle', 'ahandle')

import inspect
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar

T = TypeVar('T')
E = TypeVar('E', bound=BaseException)


async def _await_maybe(result: T | Coroutine[Any, Any, T]) -> T:
    if inspect.isawaitable(result):
        return await result
    return result


def handle(
    exc: type[E], handler: Callable[[E], Any]
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
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
    exc: type[E], handler: Callable[[E], Coroutine[Any, Any, Any]]
) -> Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]]:
    def decorator(
        func: Callable[..., Any]
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await _await_maybe(func(*args, **kwargs))
            except exc as e:
                return await handler(e)

        return wrapper

    return decorator
