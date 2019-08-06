from pybond.bond_field import BondField
from pybond.types import bond_consts
from pybond.types.bond_type import BondType


class BondSchema(BondType):
    def __init__(self, **kwargs):
        BondType.__init__(self, bond_consts.BT_STRUCT)

        fields = self.get_fields()

        if len(set(kwargs.keys()) - set(key for key, _ in fields)) > 0:
            raise Exception('Non-schema variables provided: ' +
                            ', '.join(set(kwargs.keys()) - set(key for key, _ in fields)))

        for key, field in self.get_fields():
            self.__dict__[key] = kwargs.get(key, field.default)

    @classmethod
    def get_fields(cls):
        # type: () -> List[Tuple[str, BondField]]
        if '_bond_schema_fields_' not in cls.__dict__:
            cls._bond_schema_fields_ = [
                (key, value) for key, value in cls.__dict__.items() if isinstance(value, BondField)
            ]

            cls._bond_schema_fields_.sort(key=lambda field: field[1].index)

        return cls._bond_schema_fields_

    @classmethod
    def get_field(cls, name):
        # type: (str) -> BondField
        return cls.__dict__[name]

    @classmethod
    def create_schema(cls, name, fields):
        # type: (str, Dict[str, BondField]) -> Type[BondSchema]
        schema_fields = dict(cls.__dict__)
        schema_fields.update(fields)
        return type(name, cls.__bases__, schema_fields)

    @classmethod
    def matches_schema(cls, obj):
        # type: (object) -> bool

        for key, field in cls.get_fields():
            if key not in obj.__dict__:
                if field.required:
                    return False
                continue

            if not field.field_type.matches_schema(obj.__dict__[key]):
                return False

        return True
