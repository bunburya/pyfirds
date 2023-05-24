from datetime import datetime
from enum import Enum
from typing import Optional, Callable, TypeVar, Type, Union, Generator

from dateutil import parser
from lxml import etree
from lxml.etree import Element

from pyfirds.categories import DebtSeniority, IndexTermUnit, IndexName, BaseProduct, SubProduct, FurtherSubProduct, \
    TransactionType, FinalPriceType, FxType, OptionType, DeliveryType, OptionExerciseStyle
from pyfirds.model import ReferenceData, TradingVenueAttributes, TechnicalAttributes, DebtAttributes, \
    DerivativeAttributes, PublicationPeriod, InterestRate, IndexTerm, Index, CommodityDerivativeAttributes, \
    InterestRateDerivativeAttributes, FxDerivativeAttributes, UnderlyingSingle, UnderlyingBasket, StrikePrice

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


def get_ref_data_elems(root: etree.Element) -> list[etree.Element]:
    """Get a list of `RefData` elements from the root element of a FULINS XML document."""
    return root.findall("biz_data:Pyld/document:Document/document:FinInstrmRptgRefDataRpt/document:RefData", NSMAP)


def parse_tv_attrs(elem: etree.Element, nsmap: Optional[dict[str, str]] = None) -> TradingVenueAttributes:
    """Parse a `TradgVnRltAttrbts` XML element from FIRDS into a :class:`TradingVenueAttributes` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}TradgVnRltAttrbts` or equivalent.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP
    return TradingVenueAttributes(
        trading_venue=elem.find("document:Id", nsmap).text,
        requested_admission=parse_bool(elem.find("document:IssrReq", nsmap)),
        approval_date=parse_datetime(elem.find("document:AdmssnApprvlDtByIssr", nsmap), optional=True),
        request_date=parse_datetime(elem.find("document:ReqForAdmssnDt", nsmap), optional=True),
        admission_or_first_trade_date=parse_datetime(elem.find("document:FrstTradDt", nsmap)),
        termination_date=parse_datetime(elem.find("document:TermntnDt", nsmap), optional=True)
    )


def parse_publication_period(elem: etree.Element, nsmap: Optional[dict[str, str]] = None) -> PublicationPeriod:
    """Parse a `PblctnPrd` XML element from FIRDS data into a :class:`PublicationPeriod` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}PblctnPrd` or equivalent.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP
    from_to = elem.find("document:FrDtToDt", nsmap)
    if from_to is not None:
        return PublicationPeriod(
            from_date=parse_datetime(from_to.find("document:FrDt", nsmap)),
            to_date=parse_datetime(from_to.find("document:ToDt", nsmap), optional=True)
        )
    else:
        return PublicationPeriod(
            from_date=parse_datetime(elem.find("document:FrDt", nsmap)),
            to_date=None
        )


def parse_tech_attrs(elem: etree.Element, nsmap: Optional[dict[str, str]] = None) -> TechnicalAttributes:
    """Parse a `TechAttrbts` XML element from FIRDS data into a :class:`TechnicalAttributes` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}TechAttrbts` or equivalent.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP
    return TechnicalAttributes(
        relevant_competent_authority=elem.find("document:RlvntCmptntAuthrty", nsmap).text,
        publication_period=parse_publication_period(elem.find("document:PblctnPrd", nsmap), nsmap=nsmap),
        relevant_trading_venue=elem.find("document:RlvntTradgVn", nsmap).text
    )


def parse_index_term(elem: Optional[etree.Element], optional: bool = False,
                     nsmap: Optional[dict[str, str]] = None) -> Optional[IndexTerm]:
    """Parse a `Fltg/Term` XML element from FIRDS data into a :class:`IndexTerm` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}Term`
        or equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    return IndexTerm(
        number=int(elem.find("document:Val", nsmap).text),
        unit=IndexTermUnit[elem.find("document:Unit", nsmap).text]
    )


def parse_index(elem: Optional[etree.Element], optional: bool = False,
                nsmap: Optional[dict[str, str]] = None) -> Optional[Index]:
    """Parse an `IntrstRate/Fltg` or `DerivInstrmAttrbts/UndrlygInstrm/Sngl/Indx/Nm/RefRate/Nm` XML element from FIRDS
    data into a :class:`Index` object.

    :param elem: The XML element to parse. The element should be of type `FloatingInterestRate8` as defined in the
        FULINS XSD.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    ref_rate_elem = elem.find("document:RefRate", nsmap)
    index_text = _text_or_none(ref_rate_elem.find("document:Indx", nsmap))
    if index_text is not None:
        # Try to get the appropriate IndexName enum, otherwise just treat the value as a string
        try:
            name = IndexName[index_text]
        except KeyError:
            name = index_text
    else:
        name = _text_or_none(ref_rate_elem.find("document:Nm", nsmap))
    return Index(
        isin=_text_or_none(ref_rate_elem.find("document:ISIN", nsmap)),
        name=name,
        term=parse_index_term(elem.find("document:Term", nsmap), optional=True, nsmap=nsmap)
    )


def parse_interest_rate(elem: Optional[etree.Element], optional: bool = False,
                        nsmap: Optional[dict[str, str]] = None) -> Optional[InterestRate]:
    """Parse an `IntrstRate` XML element from FIRDS data into a :class:`InterestRate` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}IntrstRate` or equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
"""
    if nsmap is None:
        nsmap = NSMAP
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    floating_elem = elem.find("document:Fltg", nsmap)
    if floating_elem is not None:
        spread = _text_or_none(floating_elem.find("document:BsisPtSprd", nsmap), wrapper=int)
    else:
        spread = None
    return InterestRate(
        fixed_rate=_text_or_none(elem.find("document:Fxd", nsmap), float),
        benchmark=parse_index(floating_elem, optional=True, nsmap=nsmap),
        spread=spread
    )


def parse_debt_attrs(elem: Optional[etree.Element], optional: bool = False,
                     nsmap: Optional[dict[str, str]] = None) -> Optional[DebtAttributes]:
    """Parse an `DebtInstrmAttrbts` XML element from FIRDS data into a :class:`DebtAttributes` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}DebtInstrmAttrbts` or equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    issued_amount_elem = elem.find("document:TtlIssdNmnlAmt", nsmap)
    return DebtAttributes(
        total_issued_amount=float(issued_amount_elem.text),
        maturity_date=parse_datetime(elem.find("document:MtrtyDt", nsmap), optional=True),
        nominal_currency=issued_amount_elem.attrib["Ccy"],
        nominal_value_per_unit=float(elem.find("document:NmnlValPerUnit", nsmap).text),
        interest_rate=parse_interest_rate(elem.find("document:IntrstRate", nsmap), nsmap=nsmap),
        seniority=_text_or_none(elem.find("document:DebtSnrty", nsmap), wrapper=DebtSeniority)
    )


def parse_commodity_deriv_attrs(
        elem: Optional[etree.Element],
        optional: bool = False,
        nsmap: Optional[dict[str, str]] = None
) -> Optional[CommodityDerivativeAttributes]:
    """Parse a `DerivInstrmAttrbts/AsstClssSpcfcAttrbts/Cmmdty` XML element from FIRDS into a
    :class:`CommodityDerivativeAttributes` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}Cmmdty`
        or equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")

    # Normal structure is `Pdct/<base product>/<sub product>/BasePdct`, but if the base product does not have an
    # associated sub product then structure will be `Pdct/<base product>/BasePdct`. So we first check for `BasePdct` two
    # levels down, if it's not there we check one level down. We also know at that point that there is no sub product
    # (and therefore no further sub product) associated.
    product_container_elem = elem.find("document:Pdct", nsmap)
    base_prod_elem = product_container_elem.find("*/*/document:BasePdct", nsmap)
    if base_prod_elem is None:
        # No sub product
        base_product = BaseProduct[product_container_elem.find("*/document:BasePdct", nsmap).text]
        sub_product = None
        further_sub_product = None
    else:
        # Sub product
        base_product = BaseProduct[base_prod_elem.text]
        product_elem = base_prod_elem.getparent()
        sub_product = _text_or_none(product_elem.find("document:SubPdct", nsmap), SubProduct)
        further_sub_product = _text_or_none(product_elem.find("document:AddtlSubPdct", nsmap), FurtherSubProduct)

    return CommodityDerivativeAttributes(
        base_product=base_product,
        sub_product=sub_product,
        further_sub_product=further_sub_product,
        transaction_type=_text_or_none(elem.find("document:TxTp", nsmap), wrapper=TransactionType),
        final_price_type=_text_or_none(elem.find("document:FnlPricTp", nsmap), wrapper=FinalPriceType)
    )


def parse_ir_attrs(elem: Optional[etree.Element], optional: bool = False,
                   nsmap: Optional[dict[str, str]] = None) -> Optional[InterestRateDerivativeAttributes]:
    """Parse a `DerivInstrmAttrbts/AsstClssSpcfcAttrbts/Intrst` XML element from FIRDS into a
    :class:`InterestRateDerivativeAttributes` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}Intrst`
        or equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    other_leg_elem = elem.find("document:OthrLegIntrstRate", nsmap)
    if other_leg_elem is not None:
        fixed_rate_2 = _text_or_none(other_leg_elem.find("document:Fxd", nsmap), wrapper=float)
        floating_rate_2 = parse_index(other_leg_elem.find("document:Fltg", nsmap), optional=True, nsmap=nsmap)
    else:
        fixed_rate_2 = None
        floating_rate_2 = None
    return InterestRateDerivativeAttributes(
        reference_rate=parse_index(elem.find("document:IntrstRate", nsmap)),
        notional_currency_2=_text_or_none(elem.find("document:OtherNtnlCcy", nsmap)),
        fixed_rate_1=_text_or_none(elem.find("document:FrstLegIntrstRate/document:Fxd", nsmap), wrapper=float),
        fixed_rate_2=fixed_rate_2,
        floating_rate_2=floating_rate_2
    )


def parse_fx_attrs(elem: Optional[etree.Element], optional: bool = False,
                   nsmap: Optional[dict[str, str]] = None) -> Optional[FxDerivativeAttributes]:
    """Parse a `DerivInstrmAttrbts/AsstClssSpcfcAttrbts/FX` XML element from FIRDS into a
    :class:`FxDerivativeAttributes` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}FX` or
        equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    return FxDerivativeAttributes(
        notional_currency_2=elem.find("document:OtherNtnlCcy", nsmap).text,
        fx_type=FxType[elem.find("document:FxTp", nsmap).text]
    )


def parse_derivative_underlying(
        elem: Optional[etree.Element],
        optional: bool = False,
        nsmap: Optional[dict[str, str]] = None
) -> Optional[Union[UnderlyingSingle, UnderlyingBasket]]:
    """Parse a `DerivInstrmAttrbts/UndrlygInstrm` XML element from FIRDS into a :class:`UnderlyingSingle` or
    :class:`UnderlyingBasket` object as appropriate.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}UndrlygInstrm` or equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP

    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")

    if (single_underlying := elem.find("document:Sngl", nsmap)) is not None:
        # An index can be represented by an ISIN or by a name and optional term. Just like our Index dataclass.
        # Annoyingly, unlike with `Fltg` elements where all three elements are combined in a single `RefRate` element,
        # here the ISIN, if present, is directly under `Indx` whereas the name and term are under `Index/Nm/RefRate`.
        index_xml = single_underlying.find("document:Indx", nsmap)
        if index_xml is None:
            index = None
        else:
            index_isin = _text_or_none(index_xml.find("document:ISIN", nsmap))
            nm = index_xml.find("document:Nm", nsmap)
            index = parse_index(nm, optional=True, nsmap=nsmap)
            if index is None:
                index = Index(isin=index_isin, name=None, term=None)
            else:
                index.isin = index_isin

        return UnderlyingSingle(
            isin=_text_or_none(single_underlying.find("document:ISIN", nsmap)),
            index=index,
            issuer_lei=_text_or_none(single_underlying.find("document:LEI", nsmap))
        )
    elif (basket_underlying := elem.find("document:Bskt", nsmap)) is not None:
        return UnderlyingBasket(
            isin=[i.text for i in basket_underlying.findall("document:ISIN", nsmap)],
            issuer_lei=[i.text for i in basket_underlying.findall("document:LEI", nsmap)]
        )
    else:
        raise ValueError("Could not find `Sngl` or `Bskt` element in `UndrlygInstrm` element.")


def parse_strike_price(elem: Optional[etree.Element], optional: bool = False,
                       nsmap: Optional[dict[str, str]] = None) -> Optional[StrikePrice]:
    """Parse a `DerivInstrmAttrbts/StrkPric` XML element from FIRDS into a :class:`StrikePrice` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}StrkPric`
        or equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP

    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    price_xml = elem.find("document:Pric", nsmap)
    if price_xml is not None:
        return StrikePrice(
            monetary_value=_text_or_none(price_xml.find("document:MntryVal/document:Amt", nsmap), wrapper=float),
            percentage=_text_or_none(price_xml.find("document:Pctg", nsmap), wrapper=float),
            yield_=_text_or_none(price_xml.find("document:Yld", nsmap), wrapper=float),
            basis_points=_text_or_none(price_xml.find("document:BsisPts", nsmap), wrapper=float),
            pending=False,
            currency=_text_or_none(price_xml.find("document:MntryVal/document:Ccy", nsmap))
        )
    else:
        no_price_xml = elem.find("document:NoPric", nsmap)
        return StrikePrice(
            monetary_value=None,
            percentage=None,
            yield_=None,
            basis_points=None,
            pending=no_price_xml.find("document:Pdg", nsmap).text == "PNDG",
            currency=_text_or_none(no_price_xml.find("document:Ccy", nsmap))
        )


def parse_derivative_attrs(elem: Optional[etree.Element], optional: bool = False,
                           nsmap: Optional[dict[str, str]] = None) -> Optional[DerivativeAttributes]:
    """Parse a `DerivInstrmAttrbts` XML element from FIRDS into a :class:`DerivativeAttributes` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}DerivInstrmAttrbts` or equivalent.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.
    """
    if nsmap is None:
        nsmap = NSMAP

    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")

    return DerivativeAttributes(
        expiry_date=parse_datetime(elem.find("document:XpryDt", nsmap), optional=True),
        price_multiplier=_text_or_none(elem.find("document:PricMltplr", nsmap), wrapper=float),
        underlying=parse_derivative_underlying(elem.find("document:UndrlygInstrm", nsmap), optional=True, nsmap=nsmap),
        option_type=_text_or_none(elem.find("document:OptnTp", nsmap), wrapper=OptionType),
        strike_price=parse_strike_price(elem.find("document:StrkPric", nsmap), optional=True, nsmap=nsmap),
        option_exercise_style=_text_or_none(elem.find("document:OptnExrcStyle", nsmap), wrapper=OptionExerciseStyle),
        delivery_type=_text_or_none(elem.find("document:DlvryTp", nsmap), wrapper=DeliveryType),
        commodity_attributes=parse_commodity_deriv_attrs(
            elem.find("document:AsstClssSpcfcAttrbts/document:Cmmdty", nsmap),
            optional=True,
            nsmap=nsmap
        ),
        ir_attributes=parse_ir_attrs(
            elem.find("document:AsstClssSpcfcAttrbts/document:Intrst", nsmap),
            optional=True,
            nsmap=nsmap
        ),
        fx_attributes=parse_fx_attrs(
            elem.find("document:AsstClssSpcfcAttrbts/document:Fx", nsmap),
            optional=True,
            nsmap=nsmap
        )
    )


R = TypeVar('R', bound=ReferenceData)


def parse_ref_data(elem: etree.Element, cls: Type[R] = ReferenceData,
                   nsmap: Optional[dict[str, str]] = None) -> R:
    """Parse a `RefData` XML element from FIRDS into a :class:`ReferenceData` object (or appropriate subclass).

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}RefData`
        or an equivalent XML element which belongs to the `document` namespace in `nsmap`.
    :param cls: The class to return. Should be a subclass of :class:`ReferenceData`.
    :param nsmap: A dict containing XML namespaces to be used when parsing `elem`.

    """
    if nsmap is None:
        nsmap = NSMAP

    gen_attrs = elem.find("document:FinInstrmGnlAttrbts", nsmap)
    return cls(
        isin=gen_attrs.find("document:Id", nsmap).text,
        full_name=gen_attrs.find("document:FullNm", nsmap).text,
        cfi=gen_attrs.find("document:ClssfctnTp", nsmap).text,
        is_commodities_derivative=parse_bool(gen_attrs.find("document:CmmdtyDerivInd", nsmap)),
        issuer_lei=elem.find("document:Issr", nsmap).text,
        fisn=gen_attrs.find("document:ShrtNm", nsmap).text,
        trading_venue_attrs=parse_tv_attrs(elem.find("document:TradgVnRltdAttrbts", nsmap), nsmap=nsmap),
        notional_currency=gen_attrs.find("document:NtnlCcy", nsmap).text,
        technical_attributes=parse_tech_attrs(elem.find("document:TechAttrbts", nsmap), nsmap=nsmap),
        debt_attributes=parse_debt_attrs(elem.find("document:DebtInstrmAttrbts", nsmap), optional=True, nsmap=nsmap),
        derivative_attributes=parse_derivative_attrs(elem.find("document:DerivInstrmAttrbts", nsmap), optional=True,
                                                     nsmap=nsmap)
    )


def iterparse(file: str, tag_to_func: Optional[dict[str, Callable[[etree.Element], R]]] = None,
              nsmap: Optional[dict[str, str]] = None) -> Generator[R, None, dict[str, int]]:
    """Parse an XML file iteratively, creating and yielding a :class:`ReferenceData` (or subclass) object from each
    relevant node, and deleting nodes as we finish with them, to preserve memory.
    :param file: Path to the XML file to parse.
    :param tag_to_func: A dict mapping each XML tag name (after the namespace bit) to the function that should be used
        to parse relevant element into a subclass of :class:`ReferenceData`.
    :param nsmap: A dict containing XML namespaces to be used when parsing the file.
    :return: A dict specifying the number of XML elements of each given tag encountered.
    """
    if tag_to_func is None:
        tag_to_func = {"RefData": parse_ref_data}
    if nsmap is None:
        nsmap = NSMAP

    # tag_to_func with namespace bits included before tags
    tag_to_func_ns = {f"{{{nsmap['document']}}}{t}": tag_to_func[t] for t in tag_to_func}

    count = {t: 0 for t in tag_to_func_ns}
    for evt, elem in etree.iterparse(file, tag=tag_to_func_ns.keys()):
        func = tag_to_func_ns[elem.tag]
        obj = func(elem, nsmap=nsmap)
        elem.clear()
        for ancestor in elem.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
        count[elem.tag] += 1
        yield obj
    return count
