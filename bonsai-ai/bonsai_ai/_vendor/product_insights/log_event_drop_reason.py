class LogEventDropReason(object):
    """
    Enum for reasons why an event was not added to the queue
    """
    EVENT_NOT_ADDED = -1
    NO_EVENTS_ACCEPTED = -2
    MAX_EVENTS_REACHED = -3
    LOG_MANAGER_NOT_INITIALIZED = -4
