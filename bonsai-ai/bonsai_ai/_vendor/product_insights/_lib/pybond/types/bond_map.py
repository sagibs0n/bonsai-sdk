from pybond.types import bond_consts
from pybond.types.bond_type import BondType


class BondMap(BondType):
    def __init__(self, key_type, value_type):
        # type: (BondType, Union[BondType, Type[BondType]]) -> None
        super(BondMap, self).__init__(bond_consts.BT_MAP)

        self.__key_type = key_type

        if not isinstance(value_type, BondType):
            self.__value_type = value_type()
        else:
            self.__value_type = value_type

    @property
    def key_bond_type(self):
        # type: () -> BondType
        return self.__key_type

    @property
    def value_bond_type(self):
        # type: () -> BondType
        return self.__value_type

    def matches_schema(self, obj):
        return issubclass(type(obj), dict)
