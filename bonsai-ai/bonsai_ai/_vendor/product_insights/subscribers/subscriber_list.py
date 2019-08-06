from __future__ import print_function

import sys
import traceback

from product_insights._type_hints import *


class SubscriberList(object):
    _subscribers = None  # type: List[Callable[[str, List[int], int], None]]

    def __init__(self):
        self._subscribers = []

    def add_subscriber(self, subscriber):
        # type: (Callable[[str, List[int], int], None]) -> None
        self._subscribers.append(subscriber)

    def clear_subscribers(self):
        # type: () -> None
        self._subscribers = []

    def update(self, tenant, sequence_ids, status):
        # type: (str, List[int], int) -> None
        for subscriber in self._subscribers:
            # noinspection PyBroadException
            try:
                subscriber(tenant, sequence_ids, status)
            except Exception as e:
                print('Subscriber Exception raised: ' + e.__class__.__name__, file=sys.stderr)
                traceback.print_exc()
