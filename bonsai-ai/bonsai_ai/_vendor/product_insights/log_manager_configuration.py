import multiprocessing

from product_insights.log_configuration import LogConfiguration

_MAX_TCP_CONNECTIONS = 6


class LogManagerConfiguration(object):
    def __init__(self, tcp_connections=3, max_events_to_batch=200, max_events_in_memory=100000, log_configuration=None,
                 drop_event_if_max_is_reached=True, batching_threads_count=multiprocessing.cpu_count(),
                 all_threads_daemon=False, update_timer=0.3, flush_timer=0.3):
        # type: (int, int, int, LogConfiguration, bool, int, bool, float, float) -> None
        """
        Creates a LogManagerConfiguration for use with a LogManager

        :param tcp_connections: Number of TCP connections we create, there will be a thread per TCP connection
        :param max_events_to_batch: Maximum number of events that are batched together
        :param max_events_in_memory: Maximum number of events to hold in memory
        :param log_configuration: LogConfiguration for Debugging purposes
        :param drop_event_if_max_is_reached: If True, old events are dropped when adding new events.
            If False, the latest event is dropped.
        :param batching_threads_count: Number of batching threads
        :param all_threads_daemon: Whether or not to set up threads as a daemon
        """
        if not 1 <= tcp_connections <= _MAX_TCP_CONNECTIONS:
            raise Exception('tcp_connections must be in range [1, {}]'.format(_MAX_TCP_CONNECTIONS))

        self.tcp_connections = tcp_connections
        self.max_events_to_batch = max_events_to_batch
        self.max_events_in_memory = max_events_in_memory
        self.log_configuration = log_configuration or LogConfiguration()
        self.drop_event_if_max_is_reached = drop_event_if_max_is_reached
        self.batching_threads_count = batching_threads_count
        self.all_threads_daemon = all_threads_daemon

        self.update_timer = update_timer  # How often the pipeline gets updated
        self.flush_timer = flush_timer  # How often the pipeline gets flushed (updated and uploaded)

        self.MAX_SIZE_ALLOWED = 3 * 1024 * 1024 - 2048

    # noinspection PyPep8Naming
    @property
    def BATCHER_TIMER(self):
        # type: () -> float
        return self.update_timer

    # noinspection PyPep8Naming
    @BATCHER_TIMER.setter
    def BATCHER_TIMER(self, value):
        # type: (float) -> None
        self.update_timer = value

    # noinspection PyPep8Naming
    @property
    def SENDER_TIMER(self):
        # type: () -> float
        return self.flush_timer

    # noinspection PyPep8Naming
    @SENDER_TIMER.setter
    def SENDER_TIMER(self, value):
        # type: (float) -> None
        self.flush_timer = value
