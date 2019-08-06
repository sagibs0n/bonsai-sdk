from collections import deque
from contextlib import contextmanager
from threading import Semaphore

from product_insights import debug, constants
from product_insights._type_hints import *
from product_insights.context import Context
from product_insights.event_counter import EventCounter
from product_insights.event_properties import EventProperties
from product_insights.event_uploader import EventUploader
from product_insights.log_manager_configuration import LogManagerConfiguration
from product_insights.poller import Poller
from product_insights.subscribers import SubscriberList, SubscriberUpdate


class LogManagerResources(object):
    __uploaders = None  # type: deque[EventUploader]
    __uploaders_semaphore = None  # type: Semaphore

    __polling_threads = None  # type: Set[Poller]

    __subscribers = None  # type: SubscriberList

    log_manager_context = None  # type: Context
    loggers = None  # type: Dict
    event_counter = None  # type: EventCounter

    def __init__(self, log_manager_configuration):
        # type: (LogManagerConfiguration) -> None
        self.__uploaders = deque(EventUploader() for _ in range(log_manager_configuration.tcp_connections))
        self.__uploaders_semaphore = Semaphore(len(self.__uploaders))

        self.loggers = {}

        if log_manager_configuration.update_timer == log_manager_configuration.flush_timer:
            self.__polling_threads = {
                Poller(log_manager_configuration.flush_timer, self._full_pipeline_update, start=True)
            }
        else:
            self.__polling_threads = {
                Poller(log_manager_configuration.update_timer, self._pipeline_batch, start=True),
                Poller(log_manager_configuration.flush_timer, self._pipeline_upload, start=True)
            }

        self.__subscribers = SubscriberList()

        self.log_manager_configuration = log_manager_configuration
        self.log_manager_context = Context()
        self.event_counter = EventCounter(log_manager_configuration.max_events_in_memory)

    def tear_down(self):
        for poller in self.__polling_threads:
            poller.stop()

        self.__uploaders = None
        self.__uploaders_semaphore = None
        self.__polling_threads = None
        self.__subscribers = None

        self.loggers = None

    @contextmanager
    def get_uploader(self):
        # type: () -> ContextManager[EventUploader]
        with self.__uploaders_semaphore:
            uploader = self.__uploaders.popleft()

            try:
                yield uploader
            except Exception as e:
                debug.handle_internal_exception(e)
            finally:
                self.__uploaders.append(uploader)

    def add_subscriber(self, subscriber):
        # type: (Callable[[str, List[int], int], None]) -> None
        self.__subscribers.add_subscriber(subscriber)

    def clear_subscribers(self):
        # type: () -> None
        self.__subscribers.clear_subscribers()

    def get_subscriber_updater(self):
        return SubscriberUpdate(self.__subscribers)

    def update_subscribers(self, tenant, sequence_id, result):
        # type: (str, Union[int, List[int]], int) -> None
        subscriber_update = self.get_subscriber_updater()
        subscriber_update.set_result(tenant, sequence_id, result)
        subscriber_update.update()

    def get_session_stats(self):
        # type: () -> EventProperties
        event = EventProperties('act_stats')

        event.set_properties({
            'sdk-version': constants.version_string,
            'S_t': constants.tenant,
            's_p': constants.os_platform,
            'S_k': constants.language_platform,
            'S_j': constants.projection,
            'S_v': constants.pi_version
        })

        event.set_property('records_received_count', self.event_counter.logged)
        event.set_property('records_tried_to_send_count',
                           self.event_counter.upload_success_count + self.event_counter.upload_failure_count)
        event.set_property('records_sent_count', self.event_counter.upload_success_count)

        event.set_property('tds', self.event_counter.bytes_uploaded)

        if self.event_counter.packages_uploaded > 0:
            event.set_property('aps', self.event_counter.bytes_uploaded / self.event_counter.packages_uploaded)
        else:
            event.set_property('aps', 0)

        return event

    def _pipeline_batch(self):
        from product_insights.pipeline import EventPipeline

        EventPipeline.process(self.loggers.keys())

    def _pipeline_upload(self):
        from product_insights.pipeline import EventPipeline

        EventPipeline.process(self.loggers.keys(), True)
        EventPipeline.upload(self.loggers.keys())

    def _full_pipeline_update(self):
        from product_insights.pipeline import EventPipeline

        EventPipeline.process(self.loggers.keys(), True)
        EventPipeline.upload(self.loggers.keys())
