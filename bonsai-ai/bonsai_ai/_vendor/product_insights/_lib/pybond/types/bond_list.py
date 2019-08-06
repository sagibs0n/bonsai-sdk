from pybond.types import bond_consts
from pybond.types.bond_schema import BondSchema
from pybond.types.bond_collection import BondCollection
from pybond.types.bond_type import BondType


class BondList(BondCollection):
    def __init__(self, element_type):
        # type: (Union[BondType, BondSchema]) -> None
        super(BondList, self).__init__(bond_consts.BT_LIST, element_type)
