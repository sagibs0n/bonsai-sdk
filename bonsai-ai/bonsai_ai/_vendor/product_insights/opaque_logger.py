from product_insights.pi_schemas import PIIKind
from product_insights.event_properties import EventProperties
from product_insights._type_hints import *


class OpaqueLogger(object):
    """
    Just the public interface exposed by the Logger class. Used to help client-side type hinting
    if they choose to use it.
    """
    def __init__(self, *args, **kwargs):
        raise Exception('Loggers MUST be created using LogManager.get_logger() or LogManager.initialize()')

    def log_event(self, event):
        # type: (Union[str, EventProperties]) -> int
        raise NotImplementedError('Must implement log_event()')

    def set_context(self, key, value, pii_kind=PIIKind.NotSet):
        # type: (str, object, int) -> None
        raise NotImplementedError('Must implement set_context()')

    def clear_context(self):
        # type: () -> None
        raise NotImplementedError('Must implement clear_context()')
