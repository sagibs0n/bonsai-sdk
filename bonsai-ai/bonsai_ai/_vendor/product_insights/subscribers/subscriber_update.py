from __future__ import print_function

import sys
import traceback

from product_insights import util
from product_insights._type_hints import *
from product_insights.subscribers import SubscriberList


class SubscriberUpdate(object):
    def __init__(self, subscribers):
        # type: (SubscriberList) -> None
        self._subscribers = subscribers

        self._results = {}  # type: Dict[str, Dict[int, List[int]]]

    def set_result(self, tenant, sequence_id, result):
        # type: (str, Union[int, List[int]], int) -> None
        if tenant not in self._results:
            self._results[tenant] = {}

        if result not in self._results[tenant]:
            self._results[tenant][result] = []

        if not util.is_iterable(sequence_id):
            sequence_id = [sequence_id]

        self._results[tenant][result].extend(sequence_id)

    def update(self):
        for tenant, results in self._results.items():
            for result, sequence_ids in results.items():
                # noinspection PyBroadException
                try:
                    self._subscribers.update(tenant, sequence_ids, result)
                except Exception as e:
                    print('Subscriber Exception raised: ' + e.__class__.__name__, file=sys.stderr)
                    traceback.print_exc()
