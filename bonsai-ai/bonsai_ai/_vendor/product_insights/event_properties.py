import re
import time

import six

from product_insights import util
from product_insights._type_hints import *
from product_insights.pi_schemas import PIIKind

_event_name_pattern = re.compile(r'^(?![_\d])[a-zA-Z0-9_]{4,100}(?<![_\d])$')
_event_prop_pattern = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9_.]{0,98}[a-zA-Z0-9])?$')


class EventProperties(object):
    name = None  # type: str

    def __init__(self, name):
        # type: (str) -> None
        if _event_name_pattern.match(name) is None:
            raise ValueError('Invalid event name ' + name)

        self.name = name

        self._timestamp = time.time()
        self._properties = {}

    def set_property(self, key, value, pii_kind=PIIKind.NotSet):
        # type: (str, Any, int) -> None
        """
        Sets the named event property to the given value. If pii_kind is specified, it will
        be handled as PII data.

        :param key: The property's name
        :param value: The property's value
        :param pii_kind: What type of PII data this value is
        """
        if _event_prop_pattern.match(key) is None:
            raise ValueError('Invalid property name ' + key)

        valid_type = self._is_valid_type(value)

        if not valid_type:
            raise Exception('Cannot set property "' + key + '" to type ' + type(value).__name__)

        self._properties[key] = (value, pii_kind)

    @staticmethod
    def _is_valid_type(obj):
        # type: (Any) -> bool
        if util.is_str(obj) or type(obj) is bytes or isinstance(obj, bool) or type(obj) in six.integer_types or \
                isinstance(obj, float):
            return True
        elif util.is_iterable(obj):
            value = list(obj)

            if len(value) > 0 and util.is_iterable(value[0]) and not util.is_str(value[0]):
                return False
            return True
        else:
            return False

    def set_properties(self, properties, pii_kind=PIIKind.NotSet):
        # type: (Dict[str, Any], int) -> None
        for key, value in properties.items():
            self.set_property(key, value, pii_kind)

    def set_timestamp(self, timestamp):
        # type: (float) -> None
        self._timestamp = timestamp

    def get_timestamp(self):
        return self._timestamp

    @property
    def properties(self):
        # type: () -> Dict[str, Tuple[object, int]]
        return self._properties.copy()
