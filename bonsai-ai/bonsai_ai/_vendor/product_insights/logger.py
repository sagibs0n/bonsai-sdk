from threading import Lock

import six

from product_insights import util
from product_insights._type_hints import *
from product_insights.pi_schemas import CsEvent, Value, PII, PIIKind, Attributes, Data, ValueKind
from product_insights.event_properties import EventProperties
from product_insights.log_event_drop_reason import LogEventDropReason
from product_insights.log_manager_resources import LogManagerResources
from product_insights.opaque_logger import OpaqueLogger
from product_insights.pipeline import EventPipeline
from product_insights.serial_number import SerialNumber


class Logger(OpaqueLogger):
    """
    Class that allows logging events for a specific tenant
    """

    _logged_tokens = set()
    _logged_tokens_lock = Lock()

    # noinspection PyMissingConstructor
    def __init__(self, source, tenant_token, log_manager_resources):
        # type: (str, str, LogManagerResources) -> None
        """
        :param source: TODO: source is not understood
        :param tenant_token: The tenant token to log events to
        """
        with Logger._logged_tokens_lock:
            if tenant_token in Logger._logged_tokens:
                raise Exception('Cannot create duplicate logger for tenant {}'.format(tenant_token))
            Logger._logged_tokens.add(tenant_token)

        self._source = source
        self._tenant_token = tenant_token
        self._sequence_id = SerialNumber(start=1)
        self._context = log_manager_resources.log_manager_context.create_child_context()

        self._event_counter = log_manager_resources.event_counter
        self._drop_old_events = log_manager_resources.log_manager_configuration.drop_event_if_max_is_reached

        self._enabled = True

    def log_event(self, event):
        # type: (Union[str, EventProperties]) -> int
        if self._event_counter.event_space_left <= 0:
            if not (self._drop_old_events and EventPipeline.drop_events(self._tenant_token)):
                return LogEventDropReason.MAX_EVENTS_REACHED

        if not self._enabled:
            raise Exception('Cannot use Logger after tearing down LogManager')

        if util.is_str(event):
            event = EventProperties(event)

        if not isinstance(event, EventProperties):
            raise Exception('Bad argument to log_event(); event must be of type EventProperties')

        sequence_id = self._sequence_id.consume()

        cs_event = self.__as_cs_event(event)
        EventPipeline.enqueue(self._tenant_token, cs_event, sequence_id)
        self._event_counter.add_logged_event()

        return sequence_id

    def set_context(self, key, value, pii_kind=PIIKind.NotSet):
        self._context.set_context(key, value, pii_kind)

    def clear_context(self):
        self._context.clear_context()

    def _disable_logger(self):
        self._enabled = False

    def __as_cs_event(self, event_properties):
        # type: (EventProperties) -> CsEvent
        properties = {}

        for properties_ in (self._context.get_context(), event_properties.properties,):
            for key, (value, pii_kind) in properties_.items():
                # noinspection PyBroadException
                try:
                    value = self.__as_bond_value(value)
                except Exception:
                    pass

                if pii_kind != PIIKind.NotSet:
                    value.attributes = Attributes(pii=PII(Kind=pii_kind))

                properties[key] = value

        return CsEvent(
            ver='3.0', time=util.time_ticks(event_properties.get_timestamp()), name=event_properties.name,
            iKey='o:' + self._tenant_token.split('-')[0], data=Data(properties=properties)
        )

    @staticmethod
    def __as_bond_value(value):
        # type: (object) -> Value
        value_kind = Logger.__get_bond_value_kind(value)

        if value_kind == ValueKind.ValueString:
            return Value(type=ValueKind.ValueString, stringValue=util.as_str(value))
        elif value_kind == ValueKind.ValueBool:
            return Value(type=ValueKind.ValueBool, longValue=bool(value))
        elif value_kind in {ValueKind.ValueUInt32, ValueKind.ValueUInt64, ValueKind.ValueInt32, ValueKind.ValueInt64}:
            return Value(type=ValueKind.ValueInt64, longValue=util.as_int(value))
        elif value_kind == ValueKind.ValueDouble:
            return Value(type=ValueKind.ValueDouble, doubleValue=float(value))

        elif value_kind == ValueKind.ValueArrayString:
            return Value(type=ValueKind.ValueArrayString, stringArray=Logger.__list_of(str, value))
        elif value_kind == ValueKind.ValueArrayBool:
            return Value(type=ValueKind.ValueArrayBool, longArray=Logger.__list_of(bool, value))
        elif value_kind in {ValueKind.ValueArrayUInt32, ValueKind.ValueArrayUInt64, ValueKind.ValueArrayInt32,
                            ValueKind.ValueArrayInt64}:
            return Value(type=ValueKind.ValueArrayInt64, longArray=Logger.__list_of(int, value))
        elif value_kind == ValueKind.ValueArrayDouble:
            return Value(type=ValueKind.ValueArrayDouble, doubleArray=Logger.__list_of(float, value))
        else:
            raise Exception('Could not interpret value_kind. This is an internal exception')

    @staticmethod
    def __list_of(type_, value):
        # type: (type, List[Any]) -> List[Any]
        return [type_(v) for v in value]

    @staticmethod
    def __get_bond_value_kind(value):
        # type: (object) -> int
        if util.is_str(value) or type(value) is bytes:
            return ValueKind.ValueString
        elif isinstance(value, bool):
            return ValueKind.ValueBool
        elif type(value) in six.integer_types:
            return ValueKind.ValueInt64
        elif isinstance(value, float):
            return ValueKind.ValueDouble
        elif util.is_iterable(value):
            # noinspection PyTypeChecker
            value = list(value)

            # Return the following value types if possible in this order:
            # 1. Exception if a list of lists (like [[3], [5], ...]  )
            # 2. The ValueArray<Type> (handling ['str'], [0], [True])
            # 3. A default ValueArrayInt64
            if len(value) > 0:
                if Logger.__get_bond_value_kind(value[0]) >= ValueKind.ValueArrayInt64:
                    raise Exception('Cannot add a list of lists')
                else:
                    return ValueKind.ValueArrayInt64 + Logger.__get_bond_value_kind(list(value)[0])
            else:
                return ValueKind.ValueArrayInt64
        else:
            raise Exception()
