from pybond.types.bond_type import BondType


class BondCollection(BondType):
    def __init__(self, bond_type_code, element_bond_type):
        # type: (int, Union[BondType, Type[BondType]]) -> None
        super(BondCollection, self).__init__(bond_type_code)

        if not isinstance(element_bond_type, BondType):
            self.__element_bond_type = element_bond_type()
        else:
            self.__element_bond_type = element_bond_type

    @property
    def element_bond_type(self):
        # type: () -> BondType
        return self.__element_bond_type

    def matches_schema(self, obj):
        try:
            # noinspection PyTypeChecker
            iter(obj)
            return True
        except TypeError:
            return False
