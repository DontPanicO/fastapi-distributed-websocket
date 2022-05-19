import sys
from abc import ABC, abstractmethod
from typing import Any, NoReturn
from collections.abc import Coroutine, Callable


__main__ = sys.modules[__name__]


class BaseMatcher(ABC):
    @abstractmethod
    def match(string: str) -> bool:
        ...


def matches(matcher: BaseMatcher, topic: str) -> bool:
    return matcher.match(topic)


def _match_topic_pattern_hash_end(pattern: str, topic: str) -> bool:
    return topic.startswith(pattern[:-1])


def _match_topic_pattern_plus_end(pattern: str, topic: str) -> bool:
    return topic.startswith(pattern[:-1]) and len(topic.split("/")) == len(
        pattern.split("/")
    )


def _match_topic_pattern_hash_start(pattern: str, topic: str) -> bool:
    return topic.endswith(pattern[1:])


def _match_topic_pattern_plus_start(pattern: str, topic: str) -> bool:
    return topic.endswith(pattern[1:]) and len(topic.split("/")) == len(
        pattern.split("/")
    )


def _match_topic_pattern_hash_middle(pattern: str, topic: str) -> bool:
    pattern_start, pattern_end = pattern.split("#")
    return topic.startswith(pattern_start) and topic.endswith(pattern_end)


def _match_topic_pattern_plus_middle(pattern: str, topic: str) -> bool:
    pattern_start, pattern_end = pattern.split("+")
    return (
        topic.startswith(pattern_start)
        and topic.endswith(pattern_end)
        and len(topic.split("/")) == len(pattern.split("/"))
    )


def _is_wildcard_pattern(pattern: str) -> bool:
    return "#" in pattern or "+" in pattern


def _check_wildcard_pattern(pattern: str) -> str:
    return "hash" if "#" in pattern else "plus" if "+" in pattern else "none"


def _check_wildcard_position(pattern: str) -> str:
    if any(pattern.endswith(suffix) for suffix in ("#", "+")):
        return "end"
    elif any(pattern.startswith(prefix) for prefix in ("#", "+")):
        return "start"
    else:
        return "middle"


def _get_matching_function(pattern: str) -> Callable[[str], bool]:
    return getattr(
        __main__,
        f"_match_topic_pattern_{_check_wildcard_pattern(pattern)}_{_check_wildcard_position(pattern)}",
    )


class TopicMatcher(BaseMatcher):
    def __init__(self, *, pattern: str) -> NoReturn:
        self._pattern = pattern

    def match(self, string: str) -> bool:
        ...
