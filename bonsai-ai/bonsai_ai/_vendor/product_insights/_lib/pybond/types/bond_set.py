from pybond.types import bond_consts, BondSchema
from pybond.types.bond_collection import BondCollection
from pybond.types.bond_type import BondType


class BondSet(BondCollection):
    def __init__(self, element_type):
        # type: (Union[BondType, BondSchema]) -> None
        super(BondSet, self).__init__(bond_consts.BT_SET, element_type.bond_type_code)
