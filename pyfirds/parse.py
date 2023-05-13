from datetime import datetime

from dateutil import parser
from lxml import etree

from pyfirds.model import ReferenceData, TradingVenueAttributes, TechnicalAttributes, DebtAttributes, \
    DerivativeAttributes

NSMAP = {
    "biz_data": "urn:iso:std:iso:20022:tech:xsd:head.003.001.01",
    "app_hdr": "urn:iso:std:iso:20022:tech:xsd:head.001.001.01",
    "document": "urn:iso:std:iso:20022:tech:xsd:auth.017.001.02"
}

def parse_bool(value: str) -> bool:
    """Parse a true or false value in the FIRDS data to a bool."""
    norm = value.lower()
    if norm == "true":
        return True
    elif norm == "false":
        return False
    else:
        raise ValueError(f"Cannot convert string '{value}' to boolean.")

def parse_datetime(value: str) -> datetime:
    """Parse a timestamp string in the FIRDS data to a datetime object."""
    return parser.parse(value)

def get_ref_data(root: etree.Element) -> list[etree.Element]:
    return root.findall("biz_data:Pyld/document:Document/document:FinInstrmRptgRefDataRpt/document:RefData", NSMAP)


def parse_tv_attrs(elem: etree.Element) -> TradingVenueAttributes:
    return TradingVenueAttributes(
        trading_venue=elem.find("document:Id", NSMAP).text,
        requested_admission=parse_bool(elem.find("document:IssrReq", NSMAP).text),
        approval_date=parse_datetime(elem.find("document:AdmssnApprvlDtByIssr", NSMAP).text),
        request_date=parse_datetime(elem.find("document:ReqForAdmssnDt", NSMAP).text),
        admission_or_first_trade_date=parse_datetime(elem.find("document:FrstTradDt", NSMAP).text),
        termination_date=parse_datetime(elem.find("document:TermntnDt", NSMAP).text)
    )


def parse_tech_attrs(elem: etree.Element) -> TechnicalAttributes:
    pass


def parse_debt_attrs(elem: etree.Element) -> DebtAttributes:
    pass


def parse_derivative_attrs(elem: etree.Element) -> DerivativeAttributes:
    pass


def parse_ref_data(elem: etree.Element) -> ReferenceData:
    gen_attrs = elem.find("document:FinInstrmGnlAttrbts", NSMAP)
    return ReferenceData(
        isin=gen_attrs.find("document:Id", NSMAP).text,
        full_name=gen_attrs.find("document:FullNm", NSMAP).text,
        cfi=gen_attrs.find("document:ClssfctnTp", NSMAP).text,
        is_commodities_derivative=parse_bool(gen_attrs.find("document:CmmdtyDerivInd")),
        issuer_lei=elem.find("document:Issr", NSMAP).text,
        fisn=gen_attrs.find("document:ShrtNm", NSMAP).text,
        trading_venue_attrs=parse_tv_attrs(elem.find("document:TradgVnRltAttrbts", NSMAP)),
        notional_currency=gen_attrs.find("document:NtnlCcy", NSMAP).text,
        technical_record_id=elem.find("document:TechRcrdId", NSMAP).text,
        technical_attributes=parse_tech_attrs(elem.find("document:TechAttrbts", NSMAP)),
        debt_attributes=parse_debt_attrs(elem.find("document:DebtInstrmAttrbts", NSMAP)),
        derivative_attributes=parse_derivative_attrs(elem.find("document:DerivInstrmAttrbts", NSMAP))
    )


