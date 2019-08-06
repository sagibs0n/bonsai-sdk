from threading import Lock


class SerialNumber(object):
    def __init__(self, start=0, step=1):
        # type: (int, int) -> None
        """
        Creates a SerialNumber object. SerialNumber is a thread-safe object used to create
        guaranteed unique serial numbers.

        :param start: The first serial number to generate
        :param step: How much to increment the value by each time
        """
        assert step != 0

        self._value = start
        self._step = step
        self._lock = Lock()

    def consume(self):
        # type: () -> int
        """
        Consumes and returns a single serial number. This function is atomic and guaranteed
        to be thread safe.

        :return:
        """
        with self._lock:
            value = self._value
            self._value += self._step

        return value
