from product_insights.pi_schemas import PIIKind


class PiiKind(object):
    """
    This class exists to map the names used from the first Python SDK to those used currently.
    """
    PiiKind_None = PIIKind.NotSet
    PiiKind_DistinguishedName = PIIKind.DistinguishedName
    PiiKind_GenericData = PIIKind.GenericData
    PiiKind_IPv4Address = PIIKind.IPv4Address
    PiiKind_IPv6Address = PIIKind.IPv6Address
    PiiKind_MailSubject = PIIKind.MailSubject
    PiiKind_PhoneNumber = PIIKind.PhoneNumber
    PiiKind_QueryString = PIIKind.QueryString
    PiiKind_SipAddress = PIIKind.SipAddress
    PiiKind_SmtpAddress = PIIKind.SmtpAddress
    PiiKind_Identity = PIIKind.Identity
    PiiKind_Uri = PIIKind.Uri
    PiiKind_Fqdn = PIIKind.Fqdn
    PiiKind_IPv4AddressLegacy = PIIKind.IPv4AddressLegacy
