"""
This is the top-level module for Product Insights. Use the imports from this module to initialize
the log manager and get loggers from it.
"""

from __future__ import absolute_import

__all__ = [
    'LogManager', 'LogManagerConfiguration', 'EventProperties', 'PiiKind', 'SubscriberStatus', 'Logger',
    'LogEventDropReason'
]
__version__ = '2.0.1'
__author__ = 'Keegan Dahm'

# This import is needed to append the path for included libraries
from . import _lib

from . import singletons as _singletons
from .event_properties import EventProperties
from .log_manager_configuration import LogManagerConfiguration
from .pii_kind import PiiKind
from .subscribers import SubscriberStatus
from .opaque_logger import OpaqueLogger as Logger
from .log_event_drop_reason import LogEventDropReason

LogManager = _singletons.customer_log_manager
