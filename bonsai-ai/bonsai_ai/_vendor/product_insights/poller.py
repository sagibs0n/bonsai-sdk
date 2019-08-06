from __future__ import print_function

import time
from threading import Thread

from product_insights._type_hints import *


class Poller(object):
    def __init__(self, interval, function, args=(), kwargs=None, start=False):
        # type: (float, Callable, List[Any], Mapping[str, Any], bool) -> None
        if kwargs is None:
            kwargs = {}

        self._continue_polling = False

        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs

        self._polling_thread = Thread(target=self._run, name=Poller._get_thread_name(function, args, kwargs), args=args,
                                      kwargs=kwargs)
        self._polling_thread.daemon = True

        if start:
            self.start()

    @staticmethod
    def _get_thread_name(function, args, kwargs):
        # type: (Callable, List[Any], Mapping[str, Any]) -> str
        name = 'Polling ' + function.__name__ + '('

        if len(args) > 0:
            name += ', '.join(str(arg) for arg in args)

        if len(kwargs) > 0:
            if len(args) > 0:
                name += ', '
            name += ', '.join(key + '=' + str(value) for key, value in kwargs.items())

        name += ')'

        return name

    def _run(self, *args, **kwargs):
        next_update = 0

        while self._continue_polling:
            if time.time() >= next_update:
                self._function(*args, **kwargs)
                next_update = time.time() + self._interval

            time.sleep(min(self._interval, 0.5))

    def start(self):
        self._continue_polling = True
        self._polling_thread.start()

    def stop(self, timeout=None):
        # type: (Optional[float]) -> bool
        self._continue_polling = False
        self._polling_thread.join(timeout)

        return not self._polling_thread.is_alive()
