from pybond.types import bond_consts
from pybond.types.bond_type import BondType


class BondEnum(BondType):
    def __init__(self):
        super(BondEnum, self).__init__(bond_consts.BT_INT32)

    @classmethod
    def get_values(cls):
        # type: () -> List[Tuple[str, int]]
        if '_bond_enum_values_' not in cls.__dict__:
            cls._bond_enum_values_ = [
                (key, value) for key, value in cls.__dict__.items() if isinstance(value, int)
            ]

            cls._bond_enum_values_.sort(key=lambda field: field[1].index)

        return cls._bond_enum_values_

    @classmethod
    def get_name(cls, value):
        for name, value_ in cls.get_values():
            if value_ == value:
                return name

        return None

    @classmethod
    def matches_schema(cls, obj):
        import pybond.types

        return pybond.types.BondInt32.matches_schema(obj) and obj in zip(*cls.get_values())[1]
