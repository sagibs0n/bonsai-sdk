import collections
import time

import six

if six.PY3:
    from typing import Any, Union


def time_ticks(now=None):
    return int((62135596800 + (now or time.time())) * 10000000)


try:
    _iterable = collections.abc.Iterable
except AttributeError:
    _iterable = collections.Iterable


def is_iterable(obj):
    return isinstance(obj, _iterable)


if six.PY2:
    def is_str(string):
        # type: (Any) -> bool
        # noinspection PyUnresolvedReferences
        return type(string) in {str, bytes, unicode}

    # noinspection PyUnresolvedReferences,PyTypeChecker
    def as_str(string):
        # type: (Union[str, bytes, unicode]) -> str
        if type(string) is unicode:
            return string.encode('utf-8')
        return string

    # noinspection PyUnresolvedReferences
    def as_bytes(string):
        # type: (Union[str, bytes, unicode]) -> bytes
        if type(string) is unicode:
            return string.encode('utf-8')
        return string

    # noinspection PyCompatibility
    def as_int(value):
        # type: (Union[int, long]) -> long
        return long(value)

else:
    def is_str(string):
        return type(string) is str

    def as_str(string):
        if type(string) is bytes:
            return string.decode()
        return string

    def as_bytes(string):
        if type(string) is str:
            return string.encode()
        return string

    def as_int(value):
        return int(value)
