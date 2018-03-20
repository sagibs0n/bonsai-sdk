from datetime import datetime
import sys
from time import time


class Logger:
    _impl = None

    def __init__(self):
        if self._impl is None:
            self._enabled_keys = {'error': True}
            self._enable_all = False
            self.__class__._impl = self.__dict__
        else:
            self.__dict__ = self._impl

    def __getattr__(self, attr):
        if self._enable_all or attr in self._enabled_keys:
            ts = datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")
            return lambda msg: \
                sys.stderr.write("[{0}][{1}] {2}\n".format(ts, attr, msg))
        else:
            return lambda msg: None

    def set_enabled(self, key):
        self.__class__._impl['_enabled_keys'][key] = True

    def set_enable_all(self, enable_all):
        self.__class__._impl['_enable_all'] = enable_all
