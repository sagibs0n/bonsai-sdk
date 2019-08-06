from collections import deque

from product_insights.pi_schemas import CsEvent
from product_insights import debug
from product_insights.pipeline.handlers.pipeline_handler import PipelineHandler
from product_insights.log_manager_resources import LogManagerResources
from product_insights.subscribers import SubscriberStatus
from pybond.encoders import compact_binary


class EventEncoder(PipelineHandler):
    def __init__(self, resource_manager, tenant_token, input_=None, output=None):
        # type: (LogManagerResources, str, deque, deque) -> None
        super(EventEncoder, self).__init__(resource_manager, tenant_token, input_, output)

    def process_input(self, flush=False):
        # type: (bool) -> None
        updater = self._resources.get_subscriber_updater()

        while len(self.input) > 0:
            cs_event, sequence_id = self.input.popleft()

            try:
                self.output.append((compact_binary.encode(cs_event, CsEvent), sequence_id))
            except Exception as e:
                debug.handle_internal_exception(e)

                updater.set_result(self._tenant_token, sequence_id, SubscriberStatus.BOND_FAILED)

        updater.update()

    def drop(self):
        dropped_ids = [item[1] for item in self.input]

        self.input.clear()
        self._resources.event_counter.drop_events(len(dropped_ids))

        self._resources.update_subscribers(self._tenant_token, dropped_ids, SubscriberStatus.EVENT_DROPPED)
