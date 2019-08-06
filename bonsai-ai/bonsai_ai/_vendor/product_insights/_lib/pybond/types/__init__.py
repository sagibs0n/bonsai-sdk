from __future__ import absolute_import

from . import bond_consts
from .bond_enum import BondEnum
from .bond_list import BondList
from .bond_map import BondMap
from .bond_nullable import BondNullable
from .bond_schema import BondSchema
from .bond_set import BondSet
from .bond_type import BondType as _BondType
from .bond_vector import BondVector


# noinspection PyShadowingBuiltins
def _test_type(obj, type):
    try:
        type(obj)
        return True
    except (ValueError, TypeError):
        return False


# Basic data types
BondBool = _BondType(bond_consts.BT_BOOL, lambda o: _test_type(o, bool) and o is not None)
BondUInt8 = _BondType(bond_consts.BT_UINT8, lambda o: _test_type(o, int) and 0 <= o <= 0xFF)
BondUInt16 = _BondType(bond_consts.BT_UINT16, lambda o: _test_type(o, int) and 0 <= o <= 0xFFFF)
BondUInt32 = _BondType(bond_consts.BT_UINT32, lambda o: _test_type(o, int) and 0 <= o <= 0xFFFFFFFF)
BondUInt64 = _BondType(bond_consts.BT_UINT64, lambda o: _test_type(o, int) and 0 <= o <= 0xFFFFFFFFFFFFFFFF)
BondFloat = _BondType(bond_consts.BT_FLOAT, lambda o: _test_type(o, float))
BondDouble = _BondType(bond_consts.BT_DOUBLE, lambda o: _test_type(o, float))
BondString = _BondType(bond_consts.BT_STRING, lambda o: type(o).__name__ in {'unicode', 'str', 'bytes'})
BondInt8 = _BondType(bond_consts.BT_INT8, lambda o: _test_type(o, int) and -0x80 <= o <= 0x7F)
BondInt16 = _BondType(bond_consts.BT_INT16, lambda o: _test_type(o, int) and -0x8000 <= o <= 0x7FFF)
BondInt32 = _BondType(bond_consts.BT_INT32, lambda o: _test_type(o, int) and -0x80000000 <= o <= 0x7FFFFFFF)
BondInt64 = _BondType(bond_consts.BT_INT64, lambda o: _test_type(o, int) and -(2 ** 63) <= o <= 2 ** 63 - 1)
BondWString = _BondType(bond_consts.BT_WSTRING, lambda o: type(o).__name__ in {'unicode', 'str', 'bytes'})
