from pybond.types import BondSchema, BondNullable, BondMap, BondString, BondInt64, BondDouble, BondUInt8
from pybond.bond_field import BondField
from pybond.types import BondVector, BondEnum


class PIIKind(BondEnum):
    NotSet = 0
    DistinguishedName = 1
    GenericData = 2
    IPv4Address = 3
    IPv6Address = 4
    MailSubject = 5
    PhoneNumber = 6
    QueryString = 7
    SipAddress = 8
    SmtpAddress = 9
    Identity = 10
    Uri = 11
    Fqdn = 12
    IPv4AddressLegacy = 13


class PII(BondSchema):
    Kind = BondField(1, PIIKind, required=False, default=PIIKind.NotSet)


class CustomerContentKind(BondEnum):
    NotSet = 0
    GenericContent = 1


class CustomerContent(BondSchema):
    Kind = BondField(1, CustomerContentKind, required=False, default=CustomerContentKind.NotSet)


class Attributes(BondSchema):
    pii = BondField(1, BondNullable(PII), required=False)
    customerContent = BondField(2, BondNullable(CustomerContent), required=False)


class ValueKind(BondEnum):
    ValueInt64 = 0
    ValueUInt64 = 1
    ValueInt32 = 2
    ValueUInt32 = 3
    ValueDouble = 4
    ValueString = 5
    ValueBool = 6
    ValueDateTime = 7
    ValueGuid = 8
    ValueArrayInt64 = 9
    ValueArrayUInt64 = 10
    ValueArrayInt32 = 11
    ValueArrayUInt32 = 12
    ValueArrayDouble = 13
    ValueArrayString = 14
    ValueArrayBool = 15
    ValueArrayDateTime = 16
    ValueArrayGuid = 17


class Value(BondSchema):
    type = BondField(1, ValueKind, required=False, default=ValueKind.ValueString)

    attributes = BondField(2, BondNullable(Attributes), required=False)
    stringValue = BondField(3, BondString, required=False, default='')
    longValue = BondField(4, BondInt64, required=False)
    doubleValue = BondField(5, BondDouble, required=False)
    guidValue = BondField(6, BondNullable(BondVector(BondUInt8)), required=False)
    stringArray = BondField(10, BondNullable(BondVector(BondString)), required=False)
    longArray = BondField(11, BondNullable(BondVector(BondInt64)), required=False)
    doubleArray = BondField(12, BondNullable(BondVector(BondDouble)), required=False)
    guidArray = BondField(13, BondNullable(BondVector(BondVector(BondUInt8))), required=False)


class Data(BondSchema):
    properties = BondField(1, BondMap(BondString, Value), required=False)


class CsEvent(BondSchema):
    ver = BondField(1, BondString)
    name = BondField(2, BondString)
    time = BondField(3, BondInt64)
    iKey = BondField(5, BondString)

    data = BondField(70, BondNullable(Data))
