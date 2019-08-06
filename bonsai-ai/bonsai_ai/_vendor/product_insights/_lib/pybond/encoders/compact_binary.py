# For documentation, look here: https://microsoft.github.io/bond/reference/cpp/compact__binary_8h_source.html
# TODO: Support both v1 and v2 collection types
import struct

from pybond import types
from pybond.bond_field import BondField
from pybond.types import BondSchema, BondList, BondNullable, BondMap, BondSet
from pybond.types import bond_consts
from pybond.types.bond_type import BondType
from pybond.types.bond_vector import BondVector


# noinspection PyProtectedMember
def _encode_field_prefix(field):
    # type: (BondField) -> bytearray
    if 0 <= field.index <= 5:
        # iiit_tttt
        return bytearray([field.index << 5 | field.field_type.bond_type_code])

    elif 5 < field.index <= 0xff:
        # 110t_tttt__iiii_iiii
        return bytearray([0b110 << 5 | field.field_type.bond_type_code, field.index])

    elif 0xff < field.index <= 0xffff:
        # 111t_tttt__iiii_iiii__iiii_iiii
        return bytearray([0b111 << 5 | field.field_type.bond_type_code, field.index & 0xff, field.index >> 8])


def _encode_bool(value):
    # type: (bool) -> bytes
    return b'\x01' if value else b'\x00'


def _encode_byte(value):
    # type: (int) -> bytearray
    return bytearray([value])


def _encode_var_uint(value):
    # type: (int) -> bytearray
    encoded = bytearray()

    while value > 0x7f:
        encoded.append(0x80 | (value & 0x7f))
        value >>= 7
    encoded.append(value)

    return encoded


def encode_zig_zag(signed, length_bytes=4):
    return (signed << 1) ^ (signed >> 8 * length_bytes - 1)


def _get_encode_var_int(length):
    # type: (int) -> Callable[int, bytearray]

    return lambda value: _encode_var_uint(encode_zig_zag(value, length_bytes=length))


def _encode_float(value):
    # type: (float) -> bytearray
    value = struct.unpack('>l', struct.pack('>f', value))[0]

    return bytearray([value & 0xff, (value >> 8) & 0xff, (value >> 16) & 0xff, (value >> 24) & 0xff])


def _encode_double(value):
    # type: (float) -> bytearray
    value = struct.unpack('>q', struct.pack('>d', value))[0]

    return bytearray([value & 0xff, (value >> 8) & 0xff, (value >> 16) & 0xff, (value >> 24) & 0xff,
                      (value >> 32) & 0xff, (value >> 40) & 0xff, (value >> 48) & 0xff, (value >> 56) & 0xff])


def _encode_string(value):
    # type: (Union[str, bytes, Iterable]) -> bytearray
    if type(value) is not bytes:
        value = value.encode('utf-8')

    return _encode_var_uint(len(value)) + value


def _encode_wstring(value):
    # type: (str) -> bytearray
    if type(value) is not bytes:
        value = value.encode('utf-16')

    return _encode_var_uint(len(value)) + value


def _encode_struct(obj, schema, base=False):
    # type: (Any, BondSchema, bool) -> bytearray
    data = bytearray()

    for key, field in schema.get_fields():  # type: (str, BondField)
        value = obj.__dict__[key]

        if not field.required and value == field.default:
            continue

        data += _encode_field_prefix(field) + _encode(field.field_type, value)

    stop = bond_consts.BT_STOP_BASE if base else bond_consts.BT_STOP
    return data + bytearray([stop])


# noinspection PyProtectedMember
def _encode_list(value, field_type):
    # type: (List[Any], BondList) -> bytearray
    data = bytearray([field_type.element_bond_type.bond_type_code]) + _encode_var_uint(len(value))

    for element in value:
        data += _encode(field_type.element_bond_type, element)

    return data


# noinspection PyProtectedMember
def _encode_map(value, field_type):
    # type: (Dict[Any], BondMap) -> bytearray
    data = bytearray([field_type.key_bond_type.bond_type_code, field_type.value_bond_type.bond_type_code]) + \
           _encode_var_uint(len(value))

    for key, element in value.items():
        data += _encode(field_type.key_bond_type, key) + _encode(field_type.value_bond_type, element)

    return data


# noinspection PyProtectedMember
def _encode(field_type, value):
    # type: (Union[BondType, Type[BondSchema]], Any) -> bytearray
    if issubclass(type(field_type), types.BondEnum):
        field_type = types.BondInt32

    if field_type in _encoders:
        return _encoders[field_type](value)
    elif type(field_type) in _collection_encoders:
        return _collection_encoders[type(field_type)](value, field_type)
    else:
        return _encode_struct(value, field_type, base=False)


def encode(obj, schema=None, base=False):
    # type: (Any, Type[BondSchema], bool) -> bytes
    if schema is None:
        assert issubclass(type(obj), BondSchema)
        schema = obj

    return bytes(_encode_struct(obj, schema, base))


_encoders = {
    types.BondBool: _encode_bool,
    types.BondUInt8: _encode_byte,
    types.BondUInt16: _encode_var_uint,
    types.BondUInt32: _encode_var_uint,
    types.BondUInt64: _encode_var_uint,
    types.BondFloat: _encode_float,
    types.BondDouble: _encode_double,
    types.BondString: _encode_string,
    types.BondInt8: _encode_byte,
    types.BondInt16: _get_encode_var_int(2),
    types.BondInt32: _get_encode_var_int(4),
    types.BondInt64: _get_encode_var_int(8),
    types.BondWString: _encode_wstring,
}  # type: Dict[BondType, Callable[Any, bytearray]]

_collection_encoders = {
    BondList: _encode_list,
    BondVector: _encode_list,
    BondSet: _encode_list,
    BondNullable: lambda value, field_type: _encode_list([value] if value is not None else [], field_type),

    BondMap: _encode_map
}  # type: Dict[Type[BondType], Callable[[BondField, Any], bytearray]]
