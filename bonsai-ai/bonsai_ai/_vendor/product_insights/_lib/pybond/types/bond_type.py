class BondType(object):
    def __init__(self, bond_type_code, schema_check=None):
        # type: (int, Callable[[object], bool]) -> None
        self.__bond_type_code = bond_type_code
        self.__schema_check = schema_check

    @property
    def bond_type_code(self):
        # type: () -> int
        return self.__bond_type_code

    def matches_schema(self, obj):
        # type: (object) -> bool
        return self.__schema_check(obj)
