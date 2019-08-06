from six.moves import range

from product_insights.subscribers import SubscriberStatus
from product_insights.pipeline.handlers.pipeline_handler import PipelineHandler


class InputBuffer(PipelineHandler):
    def process_input(self, flush=False):
        for _ in range(len(self.input)):
            self.output.append(self.input.popleft())

    def drop(self):
        dropped_ids = [item[1] for item in self.input]

        self.input.clear()
        self._resources.event_counter.drop_events(len(dropped_ids))

        self._resources.update_subscribers(self._tenant_token, dropped_ids, SubscriberStatus.EVENT_DROPPED)
