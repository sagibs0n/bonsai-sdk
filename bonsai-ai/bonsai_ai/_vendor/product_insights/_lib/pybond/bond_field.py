from pybond.types.bond_type import BondType


class BondField(object):
    field_type = None  # type: BondType

    def __init__(self, index, field_type, required=True, default=None):
        # type: (int, Union[BondType, Type[BondType]], bool, Any) -> None
        self.index = index

        if not isinstance(field_type, BondType):  # This runs if field_type is a BondSchema
            self.field_type = field_type()
        else:
            self.field_type = field_type

        self.required = required
        self.default = default
