from threading import Thread, RLock

from product_insights import proxifier
from product_insights._type_hints import *
from product_insights.log_manager_configuration import LogManagerConfiguration
from product_insights.log_manager_resources import LogManagerResources
from product_insights.logger import Logger
from product_insights.opaque_logger import OpaqueLogger
from product_insights.pii_kind import PiiKind
from product_insights.pipeline import EventPipeline


class LogManager(object):
    def __init__(self, stats_logger=None):
        # type: (OpaqueLogger) -> None
        self.__init_lock = RLock()
        self.__initialized = False

        self.__configuration = None  # type: LogManagerConfiguration
        self.__resources = None  # type: LogManagerResources

        self.__stats_logger = stats_logger

        proxifier.proxify_method(self, self.flush_and_tear_down, 'flush_and_tead_down', deprecation_warning=True)

    def initialize(self, tenant_token, log_manager_conf=None):
        # type: (str, LogManagerConfiguration) -> Optional[OpaqueLogger]
        with self.__init_lock:
            if self.__initialized:
                raise Exception('Cannot initialized LogManager when already initialized')

            self.__configuration = log_manager_conf or LogManagerConfiguration()

            self.__resources = LogManagerResources(self.__configuration)

            self.__initialized = True

        return self.get_logger(None, tenant_token)

    def tear_down(self):
        # type: () -> None
        with self.__init_lock:
            if not self.__initialized:
                raise Exception('Cannot tear down LogManager when it\'s not initialized')

            for logger in self.__resources.loggers.values():
                # noinspection PyProtectedMember
                logger._disable_logger()

            # noinspection PyProtectedMember
            with Logger._logged_tokens_lock:
                Logger._logged_tokens = set()

            self.__resources.tear_down()

            self.__initialized = False

    def get_logger(self, source, tenant_token):
        # type: (Optional[str], str) -> Optional[OpaqueLogger]
        with self.__init_lock:
            if not self.__initialized:
                # TODO: Log error
                return None

            if tenant_token not in self.__resources.loggers:
                self.__resources.loggers[tenant_token] = Logger(source, tenant_token, self.__resources)
                EventPipeline.initialize(self.__resources, tenant_token, self.__configuration.MAX_SIZE_ALLOWED)

            return self.__resources.loggers[tenant_token]

    def add_subscriber(self, subscriber):
        # type: (Callable[[str, List[int], int], None]) -> None
        with self.__init_lock:
            if not self.__initialized:
                raise Exception('Cannot add a subscriber to an uninitialized LogManager')

            self.__resources.add_subscriber(subscriber)

    def clear_subscribers(self):
        # type: () -> None
        with self.__init_lock:
            if not self.__initialized:
                raise Exception('Cannot clear subscribers from an uninitialized LogManager')

            self.__resources.clear_subscribers()

    def set_context(self, key, value, pii_kind=PiiKind.PiiKind_None):
        # type: (str, Any, Optional[int]) -> None
        with self.__init_lock:
            if not self.__initialized:
                raise Exception('Cannot set context of an uninitialized LogManager')

        if pii_kind is None:
            pii_kind = PiiKind.PiiKind_None

        self.__resources.log_manager_context.set_context(key, value, pii_kind)

    def clear_context(self):
        # type: () -> None
        with self.__init_lock:
            if not self.__initialized:
                raise Exception('Cannot clear context of an uninitialized LogManager')

        self.__resources.log_manager_context.clear_context()

    def flush(self, timeout=30):
        # type: (float) -> bool
        with self.__init_lock:
            if not self.__initialized:
                # TODO: Handle uninitialized error?
                return False

            thread = Thread(target=EventPipeline.flush, name='LogManager.flush(timeout=' + str(timeout) + ')',
                            args=(self.__resources.loggers.keys(),))
            thread.start()

            thread.join(timeout or None)

            if self.__stats_logger is not None:
                self.__send_session_stats()

            if thread.is_alive():
                # TODO: Handle killing the thread?
                return False

            return True

    def __send_session_stats(self):
        # noinspection PyBroadException
        try:
            session_stats = self.__resources.get_session_stats()

            self.__stats_logger.log_event(session_stats)
        except Exception:
            pass

    def flush_and_tear_down(self, timeout=30):
        # type: (float) -> None
        with self.__init_lock:
            self.flush(timeout)
            self.tear_down()
