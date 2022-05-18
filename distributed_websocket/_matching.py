from abc import ABC, abstractmethod
from typing import Any, NoReturn
from collections.abc import Coroutine


class BaseMatcher(ABC):
    @abstractmethod
    def match(string: str) -> bool:
        ...


def matches(matcher: BaseMatcher, topic: str) -> bool:
    return matcher.match(topic)


class TopicMatcher(BaseMatcher):
    def __init__(self, *, pattern: str) -> NoReturn:
        self._pattern = pattern
    
    def match(self, string: str) -> bool:
        ...

