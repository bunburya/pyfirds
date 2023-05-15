from datetime import datetime
from enum import Enum
from typing import Optional, Callable, Any, TypeVar, Type, Union

from dateutil import parser
from lxml import etree

from pyfirds.categories import DebtSeniority, IndexTermUnit, IndexName, BaseProduct, SubProduct, FurtherSubProduct
from pyfirds.model import ReferenceData, TradingVenueAttributes, TechnicalAttributes, DebtAttributes, \
    DerivativeAttributes, PublicationPeriod, InterestRate, IndexTerm, Index, CommodityDerivativeAttributes

NSMAP = {
    "biz_data": "urn:iso:std:iso:20022:tech:xsd:head.003.001.01",
    "app_hdr": "urn:iso:std:iso:20022:tech:xsd:head.001.001.01",
    "document": "urn:iso:std:iso:20022:tech:xsd:auth.017.001.02"
}

T = TypeVar("T")


def _text_or_none(
        elem: Optional[etree.Element],
        wrapper: Optional[Union[Callable[[str], T], Type[Enum]]] = None) -> Optional[Union[T, Enum, str]]:
    """A convenience function that takes an XML element or None, and returns the element's text if it exists or None
    otherwise.

    :param elem: The XML element or None.
    :param wrapper: A function or :class:`enum.Enum` subtype to be used to process the XML element's text. If a
        function, it will be called with the text and the result will be returned. If an Enum subtype, a member of the
        subtype with a name corresponding to the text will be returned.
    """
    if elem is None:
        return None
    else:
        text = elem.text
        if wrapper is None:
            return text
        elif issubclass(wrapper, Enum):
            return wrapper[text]
        else:
            return wrapper(text)


def parse_bool(elem: Optional[etree.Element], optional: bool = False) -> Optional[bool]:
    """Parse a true or false value in the FIRDS data to a bool.

    :param elem: XML element which contains the text value to parse, namely "true" or "false" as used in FIRDS.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.

    """
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    value = elem.text.lower()
    if value == "true":
        return True
    elif value == "false":
        return False
    else:
        raise ValueError(f"Cannot convert string '{value}' to boolean.")


def parse_datetime(elem: Optional[etree.Element], optional: bool = False) -> Optional[datetime]:
    """Parse a timestamp string in the FIRDS data to a datetime object.

    :param elem: XML element which contains the text value to parse, in ISO 8601 date format as used in FIRDS.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    """
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    value = elem.text
    return parser.parse(value)


def get_ref_data(root: etree.Element) -> list[etree.Element]:
    return root.findall("biz_data:Pyld/document:Document/document:FinInstrmRptgRefDataRpt/document:RefData", NSMAP)


def parse_tv_attrs(elem: etree.Element) -> TradingVenueAttributes:
    """Parse a `TradgVnRltAttrbts` XML element from FIRDS into a :class:`TradingVenueAttributes` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}TradgVnRltAttrbts`.
    """
    return TradingVenueAttributes(
        trading_venue=elem.find("document:Id", NSMAP).text,
        requested_admission=parse_bool(elem.find("document:IssrReq", NSMAP)),
        approval_date=parse_datetime(elem.find("document:AdmssnApprvlDtByIssr", NSMAP)),
        request_date=parse_datetime(elem.find("document:ReqForAdmssnDt", NSMAP)),
        admission_or_first_trade_date=parse_datetime(elem.find("document:FrstTradDt", NSMAP)),
        termination_date=parse_datetime(elem.find("document:TermntnDt", NSMAP))
    )


def parse_publication_period(elem: etree.Element) -> PublicationPeriod:
    """Parse a `PblctnPrd` XML element from FIRDS data into a :class:`PublicationPeriod` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}PblctnPrd`.
    """
    from_to = elem.find("document:FrDt", NSMAP)
    if from_to is not None:
        return PublicationPeriod(
            from_date=parse_datetime(from_to.find("document:FrDt", NSMAP)),
            to_date=parse_datetime(from_to.find("document:ToDt", NSMAP), optional=True)
        )
    else:
        return PublicationPeriod(
            from_date=parse_datetime(elem.find("document:FrDt", NSMAP)),
            to_date=None
        )


def parse_tech_attrs(elem: etree.Element) -> TechnicalAttributes:
    """Parse a `TechAttrbts` XML element from FIRDS data into a :class:`TechnicalAttributes` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}TechAttrbts`.
    """
    return TechnicalAttributes(
        is_inconsistent=parse_bool(elem.find("document:IncnsstncyInd", NSMAP).text),
        last_update=parse_datetime(elem.find("document:LstUpdt", NSMAP).text),
        submission_date_time=parse_datetime(elem.find("document:SubmissnDtTm", NSMAP), optional=True),
        relevant_competent_authority=elem.find("document:RlvntCmptntAuthrty", NSMAP).text,
        publication_period=parse_publication_period(elem.find("document:PblctnPrd", NSMAP)),
        never_published=parse_bool(elem.find("document:NvrPblshd", NSMAP))
    )


def parse_index_term(elem: Optional[etree.Element], optional: bool = False) -> Optional[IndexTerm]:
    """Parse a `Fltg/Term` XML element from FIRDS data into a :class:`IndexTerm` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}Term`.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    """
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    return IndexTerm(
        number=int(elem.find("document:Val", NSMAP).text),
        unit=IndexTermUnit[elem.find("document:Unit", NSMAP).text]
    )


def parse_index(elem: Optional[etree.Element], optional: bool = False) -> Optional[Index]:
    """Parse an `IntrstRate/Fltg` XML element from FIRDS data into a :class:`Index` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}Fltg`.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    """
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    ref_rate_elem = elem.find("document:RefRate", NSMAP)
    index_text = _text_or_none(ref_rate_elem.find("document:Index", NSMAP))
    if index_text is not None:
        # Try to get the appropriate IndexName enum, otherwise just treat the value as a string
        try:
            name = IndexName[index_text]
        except KeyError:
            name = index_text
    else:
        name = _text_or_none(ref_rate_elem.find("document:Nm", NSMAP))
    return Index(
        isin=_text_or_none(ref_rate_elem.find("document:ISIN", NSMAP)),
        name=name,
        term=parse_index_term(elem.find("document:Term", NSMAP), optional=True)
    )


def parse_interest_rate(elem: etree.Element) -> InterestRate:
    """Parse an `IntrstRate` XML element from FIRDS data into a :class:`InterestRate` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}IntrstRate`."""
    floating_elem = elem.find("document:Fltg", NSMAP)
    return InterestRate(
        fixed_rate=_text_or_none(elem.find("document:Fxd", NSMAP), float),
        benchmark=parse_index(floating_elem, optional=True),
        spread=_text_or_none(floating_elem.find("document:BsisPtSprd"), int)
    )


def parse_debt_attrs(elem: Optional[etree.Element], optional: bool = False) -> Optional[DebtAttributes]:
    """Parse an `DebtInstrmAttrbts` XML element from FIRDS data into a :class:`DebtAttributes` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}DebtInstrmAttrbts`.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    """
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    return DebtAttributes(
        total_issued_amount=float(elem.find("document:TtlIssdNmnlAmt", NSMAP).text),
        maturity_date=parse_datetime(elem.find("document:MtrtyDt", NSMAP), optional=True),
        nominal_currency=elem.find("document:TtlIssdNmnlAmt/document:@Ccy").text,
        nominal_value_per_unit=float(elem.find("document:NmnlValPerUnit", NSMAP).text),
        interest_rate=parse_interest_rate(elem.find("document:IntrstRate", NSMAP)),
        seniority=DebtSeniority[elem.find("document:DebtSnrty", NSMAP).text]
    )

def parse_commodity_deriv_attrs(
        elem: Optional[etree.Element],
        optional: bool = False
) -> Optional[CommodityDerivativeAttributes]:
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    product_elem = elem.find("document:Pdct/*/*", NSMAP)
    return CommodityDerivativeAttributes(
        base_product=BaseProduct[product_elem.find("document:BasePdct", NSMAP).text],
        sub_product=_text_or_none(product_elem.find("document:SubPdct", NSMAP), SubProduct),
        further_sub_product=_text_or_none(product_elem.find("document:AddtlSubPdct", NSMAP), FurtherSubProduct),
        # TODO
    )


def parse_derivative_attrs(elem: etree.Element) -> DerivativeAttributes:
    pass


def parse_ref_data(elem: etree.Element) -> ReferenceData:
    """Parse a `RefData` XML element from FIRDS into a :class:`ReferenceData` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}RefData`.
    """
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
        debt_attributes=parse_debt_attrs(elem.find("document:DebtInstrmAttrbts", NSMAP), optional=True),
        derivative_attributes=parse_derivative_attrs(elem.find("document:DerivInstrmAttrbts", NSMAP))
    )
