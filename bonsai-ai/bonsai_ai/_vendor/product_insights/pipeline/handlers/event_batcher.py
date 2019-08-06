from collections import deque

from product_insights.subscribers import SubscriberStatus
from product_insights._type_hints import *
from product_insights.pipeline.handlers.pipeline_handler import PipelineHandler
from product_insights.log_manager_resources import LogManagerResources


class EventBatcher(PipelineHandler):
    _package = None  # type: List[bytes]
    _events = None  # type: List[int]

    def __init__(self, resource_manager, tenant_token, max_package_size, max_batch_size, input_=None, output=None):
        # type: (LogManagerResources, str, int, int, deque, deque) -> None
        super(EventBatcher, self).__init__(resource_manager, tenant_token, input_, output)

        self._max_package_size = max_package_size
        self._max_batch_size = max_batch_size

        self._package = []
        self._package_length = 0
        self._events = []

    def process_input(self, flush=False):
        # type: (bool) -> None
        while len(self.input) > 0:
            cs_event, sequence_id = self.input.popleft()

            if self._package_length + len(cs_event) > self._max_package_size or \
                    len(self._events) >= self._max_batch_size:
                self._emit_package()

            self._package.append(cs_event)
            self._package_length += len(cs_event)
            self._events.append(sequence_id)

        if flush and len(self._package) > 0:
            self._emit_package()

    def _emit_package(self):
        self.output.append((b''.join(self._package), self._events))
        self._package = []
        self._package_length = 0
        self._events = []

    def drop(self):
        dropped_ids = [item[1] for item in self.input]

        self.input.clear()
        self._resources.event_counter.drop_events(len(dropped_ids))

        self._resources.update_subscribers(self._tenant_token, dropped_ids, SubscriberStatus.EVENT_DROPPED)
