from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Union

from lxml import etree

from pyfirds.categories import DebtSeniority, OptionType, OptionExerciseStyle, DeliveryType, BaseProduct, SubProduct, \
    FurtherSubProduct, IndexTermUnit, TransactionType, FinalPriceType, FxType, IndexName, StrikePriceType
from pyfirds.xml_utils import parse_bool, optional, parse_datetime, text_or_none, parse_date, XmlParsed


@dataclass(slots=True)
class IndexTerm(XmlParsed):
    """The term of an index or benchmark.
    """

    number: int
    """The number of weeks, months, etc (as determined by `unit`)."""
    unit: IndexTermUnit
    """The unit of time in which the term is expressed (days, weeks, months or years)."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> 'IndexTerm':
        """Parse a `Fltg/Term` XML element from FIRDS data into a :class:`IndexTerm` object.

        :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}Term`
            or equivalent.
        """
        nsmap = elem.nsmap
        return IndexTerm(
            number=int(elem.find("Val", nsmap).text),
            unit=IndexTermUnit[elem.find("Unit", nsmap).text]
        )

@dataclass(slots=True)
class StrikePrice(XmlParsed):
    """The strike price of a derivative instrument.
    """

    price_type: StrikePriceType
    """How the price is expressed (as a monetary value, percentage, yield or basis points). Alternatively identifies if
    no price is available."""
    price: Optional[float]
    """The actual price, expressed according to `price_type`. Will be `None` if no price is available."""
    pending: bool
    """Whether the price is currently not available and is pending."""
    currency: Optional[str]
    """The currency in which the price is denominated (if appropriate)."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> 'StrikePrice':
        """Parse a `DerivInstrmAttrbts/StrkPric` XML element from FIRDS into a :class:`StrikePrice` object.

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}StrkPric` or equivalent.
        """
        nsmap = elem.nsmap
        price_xml = elem.find("Pric", nsmap)
        if price_xml is not None:
            if (val_xml := price_xml.find("MntryVal/Amt", nsmap)) is not None:
                price_type = StrikePriceType.MONETARY_VALUE
            elif (val_xml := price_xml.find("Pctg", nsmap)) is not None:
                price_type = StrikePriceType.PERCENTAGE
            elif (val_xml := price_xml.find("Yld", nsmap)) is not None:
                price_type = StrikePriceType.YIELD
            elif (val_xml := price_xml.find("BsisPts", nsmap)) is not None:
                price_type = StrikePriceType.BASIS_POINTS
            else:
                raise ValueError("`Pric` element present but no price identified when parsing `StrkPric` element.")
            price = text_or_none(val_xml, wrapper=float)

            return StrikePrice(
                price_type=price_type,
                price=price,
                pending=False,
                currency=text_or_none(price_xml.find("MntryVal/Ccy", nsmap))
            )
        else:
            no_price_xml = elem.find("NoPric", nsmap)
            return StrikePrice(
                price_type=StrikePriceType.NO_PRICE,
                price=None,
                pending=no_price_xml.find("Pdg", nsmap).text == "PNDG",
                currency=text_or_none(no_price_xml.find("Ccy", nsmap))
            )


@dataclass(slots=True)
class Index(XmlParsed):
    """An index or benchmark rate that is used in the reference data for certain financial instruments.
    """

    name: Optional[Union[str, IndexName]]
    """The name of the index or benchmark. Should either be a :class:`IndexName` object or a 25 character string."""
    isin: Optional[str]
    """The ISIN of the index or benchmark."""
    term: Optional[IndexTerm]
    """The term of the index or benchmark."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> 'Index':
        """Parse an `IntrstRate/Fltg` or `DerivInstrmAttrbts/UndrlygInstrm/Sngl/Indx/Nm/RefRate/Nm` XML element from
        FIRDS data into a :class:`Index` object.

        :param elem: The XML element to parse. The element should be of type `FloatingInterestRate8` as defined in the
            FULINS XSD.
        """

        nsmap = elem.nsmap
        ref_rate_elem = elem.find("RefRate", nsmap)
        index_text = text_or_none(ref_rate_elem.find("Indx", nsmap))
        if index_text is not None:
            # Try to get the appropriate IndexName enum, otherwise just treat the value as a string
            try:
                name = IndexName[index_text]
            except KeyError:
                name = index_text
        else:
            name = text_or_none(ref_rate_elem.find("Nm", nsmap))
        return Index(
            isin=text_or_none(ref_rate_elem.find("ISIN", nsmap)),
            name=name,
            term=optional(elem.find("Term", nsmap), IndexTerm)
        )


@dataclass(slots=True)
class TradingVenueAttributes(XmlParsed):
    """Data relating to the trading or admission to trading of a financial instrument on a trading venue.
    """

    trading_venue: str  # TODO: MIC class? https://www.iso20022.org/market-identifier-codes
    """The Market Identifier Code (ISO 20022) for the trading venue or systemic internaliser. A segment MIC is used
    where available; otherwise, an operating MIC is used."""
    requested_admission: bool
    """Whether the issuer has requested or approved the trading or admission to trading of their financial instruments
    on a trading venue."""
    approval_date: Optional[datetime]
    """Date and time the issuer has approved admission to trading or trading in its financial instruments on a trading
    venue."""
    request_date: Optional[datetime]
    """Date and time of the request for admission to trading on the trading venue."""
    admission_or_first_trade_date: Optional[datetime]
    """Date and time of the admission to trading on the trading venue or the date and time when the instrument was first
    traded or an order or quote was first received by the trading venue."""
    termination_date: Optional[datetime]
    """Date and time when the instrument ceases to be traded or admitted to trading on the trading venue."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "TradingVenueAttributes":
        """Parse a `TradgVnRltAttrbts` XML element from FIRDS into a :class:`TradingVenueAttributes` object.

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}TradgVnRltAttrbts` or equivalent.
        """
        nsmap = elem.nsmap
        return TradingVenueAttributes(
            trading_venue=elem.find("Id", nsmap).text,
            requested_admission=parse_bool(elem.find("IssrReq", nsmap)),
            approval_date=parse_datetime(elem.find("AdmssnApprvlDtByIssr", nsmap), optional=True),
            request_date=parse_datetime(elem.find("ReqForAdmssnDt", nsmap), optional=True),
            admission_or_first_trade_date=parse_datetime(elem.find("FrstTradDt", nsmap)),
            termination_date=parse_datetime(elem.find("TermntnDt", nsmap), optional=True)
        )


@dataclass(slots=True)
class InterestRate(XmlParsed):
    """Data about the interest rate applicable to a debt instrument.
    """

    fixed_rate: Optional[float]
    """The interest rate payable on a fixed rate instrument, expressed as a percentage (eg, 7.5 means 7.5% interest rate)."""
    benchmark: Optional[Index]
    """The benchmark or index of a floating rate instrument."""
    spread: Optional[int]
    """Spread of a floating rate instrument, expressed as an integer number of basis points."""

    def validate(self):
        """Check that either a fixed rate or a floating rate is defined."""
        assert (self.fixed_rate is not None) or ((self.benchmark is not None) and self.spread is not None)

    @property
    def is_fixed(self) -> bool:
        """Whether this interest rate is a fixed interest rate."""
        return self.fixed_rate is not None

    @property
    def is_floating(self) -> bool:
        """Whether this interest rate is a floating interest rate."""
        return self.benchmark is not None

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "InterestRate":
        """Parse an `IntrstRate` XML element from FIRDS data into an :class:`InterestRate` object.

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}IntrstRate` or equivalent.
        """
        nsmap = elem.nsmap
        floating_elem = elem.find("Fltg", nsmap)
        if floating_elem is not None:
            spread = text_or_none(floating_elem.find("BsisPtSprd", nsmap), wrapper=int)
        else:
            spread = None
        return InterestRate(
            fixed_rate=text_or_none(elem.find("Fxd", nsmap), float),
            benchmark=optional(floating_elem, Index),
            spread=spread
        )


@dataclass(slots=True)
class PublicationPeriod(XmlParsed):
    """The period for which details on a financial instrument were published.
    """

    from_date: date
    """The date from which details on the financial instrument were published."""
    to_date: Optional[date]
    """The date to which details on the financial instrument were published."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "PublicationPeriod":
        """Parse a `PblctnPrd` XML element from FIRDS data into a :class:`PublicationPeriod` object.

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}PblctnPrd` or equivalent.
        """
        nsmap = elem.nsmap
        from_to = elem.find("FrDtToDt", nsmap)
        if from_to is not None:
            return PublicationPeriod(
                from_date=parse_date(from_to.find("FrDt", nsmap)),
                to_date=parse_date(from_to.find("ToDt", nsmap), optional=True)
            )
        else:
            return PublicationPeriod(
                from_date=parse_date(elem.find("FrDt", nsmap)),
                to_date=None
            )


@dataclass(slots=True)
class TechnicalAttributes(XmlParsed):
    """The technical attributes of a financial instrument (ie, attributes relating to the submission of details of the
    financial instrument to FIRDS).
    """

    relevant_competent_authority: Optional[str]
    """The relevant competent authority for the instrument."""
    # publication_period does not appear in TermntdRcrd, so is optional. But should appear in ReferenceData classes.
    publication_period: Optional[PublicationPeriod]
    """The period for which these details on the financial instrument was published.
    NOTE: `publication_period` is optional as it does not appear in :class:`TerminatedRecord` classes, but it should
    always appear in :class:`ReferenceData` classes."""
    relevant_trading_venue: Optional[str]
    """The MIC of the trading venue that reported the record considered as the reference for the published data."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "TechnicalAttributes":
        """Parse a `TechAttrbts` XML element from FIRDS data into a :class:`TechnicalAttributes` object.

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}TechAttrbts` or equivalent.
        """
        nsmap = elem.nsmap
        return TechnicalAttributes(
            relevant_competent_authority=text_or_none(elem.find("RlvntCmptntAuthrty", nsmap)),
            publication_period=optional(elem.find("PblctnPrd", nsmap), PublicationPeriod),
            relevant_trading_venue=text_or_none(elem.find("RlvntTradgVn", nsmap))
        )


@dataclass(slots=True)
class DebtAttributes(XmlParsed):
    """Reference data for bonds or other forms of securitised debt.
    """
    total_issued_amount: float
    """The total issued nominal amount of the financial instrument. Amount is expressed in the `nominal_currency`."""
    maturity_date: Optional[date]
    """The maturity date of the financial instrument. Only applies to debt instruments with defined maturity."""
    nominal_currency: str
    """The currency of the nominal value."""
    nominal_value_per_unit: float
    """The nominal value of each traded unit. If not available, the minimum traded amount is included.
    Amount is expressed in the `nominal_currency`."""
    interest_rate: InterestRate
    """Details of the interest rate applicable to the financial instrument."""
    seniority: Optional[DebtSeniority]
    """The seniority of the financial instrument (senior, mezzanine, subordinated or junior)."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "DebtAttributes":
        nsmap = elem.nsmap
        issued_amount_elem = elem.find("TtlIssdNmnlAmt", nsmap)
        return DebtAttributes(
            total_issued_amount=float(issued_amount_elem.text),
            maturity_date=parse_date(elem.find("MtrtyDt", nsmap), optional=True),
            nominal_currency=issued_amount_elem.attrib["Ccy"],
            nominal_value_per_unit=float(elem.find("NmnlValPerUnit", nsmap).text),
            interest_rate=InterestRate.from_xml(elem.find("IntrstRate", nsmap)),
            seniority=text_or_none(elem.find("DebtSnrty", nsmap), wrapper=DebtSeniority)
        )


@dataclass(slots=True)
class CommodityDerivativeAttributes(XmlParsed):
    """Additional reference data for a commodity derivative instrument.
    """
    base_product: BaseProduct
    """The base product for the underlying asset class."""
    sub_product: Optional[SubProduct]
    """The sub-product for the underlying asset class."""
    further_sub_product: Optional[FurtherSubProduct]
    """The further sub-product (ie, sub-sub-product) for the underlying asset class."""
    transaction_type: Optional[TransactionType]
    """The transaction type as specified by the trading venue."""
    final_price_type: Optional[FinalPriceType]
    """The final price type as specified by the trading venue."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> 'CommodityDerivativeAttributes':
        """Parse a `DerivInstrmAttrbts/AsstClssSpcfcAttrbts/Cmmdty` XML element from FIRDS into a
        :class:`CommodityDerivativeAttributes` object.

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}Cmmdty` or equivalent.
        """
        # Normal structure is `Pdct/<base product>/<sub product>/BasePdct`, but if the base product does not have an
        # associated sub product then structure will be `Pdct/<base product>/BasePdct`. So we first check for
        # `BasePdct` two levels down, if it's not there we check one level down. We also know at that point that
        # there is no sub product (and therefore no further sub product) associated.
        nsmap = elem.nsmap
        product_container_elem = elem.find("Pdct", nsmap)
        base_prod_elem = product_container_elem.find("*/*/BasePdct", nsmap)
        if base_prod_elem is None:
            # No sub product
            base_product = BaseProduct[product_container_elem.find("*/BasePdct", nsmap).text]
            sub_product = None
            further_sub_product = None
        else:
            # Sub product
            base_product = BaseProduct[base_prod_elem.text]
            product_elem = base_prod_elem.getparent()
            sub_product = text_or_none(product_elem.find("SubPdct", nsmap), SubProduct)
            further_sub_product = text_or_none(product_elem.find("AddtlSubPdct", nsmap), FurtherSubProduct)

        return CommodityDerivativeAttributes(
            base_product=base_product,
            sub_product=sub_product,
            further_sub_product=further_sub_product,
            transaction_type=text_or_none(elem.find("TxTp", nsmap), wrapper=TransactionType),
            final_price_type=text_or_none(elem.find("FnlPricTp", nsmap), wrapper=FinalPriceType)
        )


@dataclass(slots=True)
class InterestRateDerivativeAttributes(XmlParsed):
    """Additional reference data for an interest rate derivative instrument.
    """
    reference_rate: Index
    """The reference rate."""
    notional_currency_2: Optional[str]
    """In the case of multi-currency or cross-currency swaps the currency in which leg 2 of the contract is denominated.
    For swaptions where the underlying swap is multi-currency, the currency in which leg 2 of the swap is denominated."""
    fixed_rate_1: Optional[float]
    """The fixed rate of leg 1 of the trade, if applicable. Expressed as a percentage."""
    fixed_rate_2: Optional[float]
    """The fixed rate of leg 2 of the trade, if applicable. Expressed as a percentage."""
    floating_rate_2: Optional[Index]
    """The floating rate of leg 2 of the trade, if applicable."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "InterestRateDerivativeAttributes":
        """Parse a `DerivInstrmAttrbts/AsstClssSpcfcAttrbts/Intrst` XML element from FIRDS into a
        :class:`InterestRateDerivativeAttributes` object.

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}Intrst` or equivalent.
        """
        nsmap = elem.nsmap
        other_leg_elem = elem.find("OthrLegIntrstRate", nsmap)
        if other_leg_elem is not None:
            fixed_rate_2 = text_or_none(other_leg_elem.find("Fxd", nsmap), wrapper=float)
            floating_rate_2 = optional(other_leg_elem.find("Fltg", nsmap), Index)
        else:
            fixed_rate_2 = None
            floating_rate_2 = None
        return InterestRateDerivativeAttributes(
            reference_rate=Index.from_xml(elem.find("IntrstRate", nsmap)),
            notional_currency_2=text_or_none(elem.find("OtherNtnlCcy", nsmap)),
            fixed_rate_1=text_or_none(elem.find("FrstLegIntrstRate/Fxd", nsmap), wrapper=float),
            fixed_rate_2=fixed_rate_2,
            floating_rate_2=floating_rate_2
        )


@dataclass(slots=True)
class FxDerivativeAttributes(XmlParsed):
    """Additional reference data for a foreign exchange derivative instrument.
    """
    notional_currency_2: str
    """The second currency of the currency pair."""
    fx_type: FxType
    """The type of underlying currency."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "FxDerivativeAttributes":
        """Parse a `DerivInstrmAttrbts/AsstClssSpcfcAttrbts/FX` XML element from FIRDS into a
        :class:`FxDerivativeAttributes` object.

        :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}FX` or
            equivalent.
        """
        nsmap = elem.nsmap
        return FxDerivativeAttributes(
            notional_currency_2=elem.find("OtherNtnlCcy", nsmap).text,
            fx_type=FxType[elem.find("FxTp", nsmap).text]
        )


@dataclass(slots=True)
class UnderlyingSingle:
    """Reference data for a single asset which underlies a derivative instrument.
    """

    isin: Optional[str]
    """The ISIN of the underlying financial instrument.
        - For ADRs, GDRs and similar instruments, the ISIN code of the financial instrument on which those instruments
        are based. For convertible bonds, the ISIN code of the instrument in which the bond can be converted.
        - For derivatives or other instruments which have an underlying, the underlying instrument ISIN code, when the
        underlying is admitted to trading, or traded on a trading venue. Where the underlying is a stock dividend, then
        the ISIN code of the related share entitling the underlying dividend shall be provided.
        - For Credit Default Swaps, the ISIN of the reference obligation shall be provided."""
    index: Optional[Union[str, Index]]
    """The ISIN, or an :class:`Index` object, representing the underlying index."""
    issuer_lei: Optional[str]
    """The LEI of the underlying issuer."""


@dataclass(slots=True)
class UnderlyingBasket:
    """Reference data for a basket of assets which underlie a derivative instrument.
    """

    isin: Optional[list[str]]
    """A list of ISINs of the financial instruments in the basket."""
    issuer_lei: Optional[list[str]]
    """A list of LEIs of issuers in the basket."""


@dataclass(slots=True)
class DerivativeUnderlying(XmlParsed):
    """Reference data for the asset underlying a derivative. The underlying may be a single issuer, instrument or index,
    or may be a basket of instruments or issuers. The relevant parameter will be populated and the rest will be None.
    """

    single: Optional[UnderlyingSingle]
    """Data for a single instrument, index or issuer underlying a derivative instrument, or None if the underlying is a
    basket."""
    basket: Optional[UnderlyingBasket]
    """Data for a basket of instruments or issuers underlying a derivative instrument, or None if the underlying is a
    single instrument, index or issuer."""

    @classmethod
    def from_xml(cls, elem: [etree.Element]) -> "DerivativeUnderlying":
        """Parse a `DerivInstrmAttrbts/UndrlygInstrm` XML element from FIRDS into a :class:`UnderlyingSingle` or
        :class:`UnderlyingBasket` object as appropriate.

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}UndrlygInstrm` or equivalent.
        """

        nsmap = elem.nsmap
        single = basket = None
        if (single_underlying := elem.find("Sngl", nsmap)) is not None:
            # An index can be represented by an ISIN or by a name and optional term. Just like our Index dataclass.
            # Annoyingly, unlike with `Fltg` elements where all three elements are combined in a single `RefRate`
            # element, here the ISIN, if present, is directly under `Indx` whereas the name and term are under
            # `Index/Nm/RefRate`.
            index_xml = single_underlying.find("Indx", nsmap)
            if index_xml is None:
                index = None
            else:
                index_isin = text_or_none(index_xml.find("ISIN", nsmap))
                index = optional(index_xml.find("Nm", nsmap), Index)
                if index is None:
                    index = Index(isin=index_isin, name=None, term=None)
                else:
                    index.isin = index_isin

            single = UnderlyingSingle(
                isin=text_or_none(single_underlying.find("ISIN", nsmap)),
                index=index,
                issuer_lei=text_or_none(single_underlying.find("LEI", nsmap))
            )
        elif (basket_underlying := elem.find("Bskt", nsmap)) is not None:
            basket = UnderlyingBasket(
                isin=[i.text for i in basket_underlying.findall("ISIN", nsmap)],
                issuer_lei=[i.text for i in basket_underlying.findall("LEI", nsmap)]
            )
        else:
            raise ValueError("Could not find `Sngl` or `Bskt` element in `UndrlygInstrm` element.")
        return DerivativeUnderlying(
            single=single,
            basket=basket
        )


@dataclass(slots=True)
class DerivativeAttributes(XmlParsed):
    """Reference data for a derivative instrument.

    Note that some other types of instrument can also have derivative-related attributes, eg, some collective investment
    scheme (CFI code C) instruments.
    """

    expiry_date: Optional[date]
    """Expiry date of the instrument."""
    price_multiplier: Optional[float]
    """Number of units of the underlying instrument represented by a single derivative contract. For a future or option
    on an index, the amount per index point."""
    underlying: Optional[DerivativeUnderlying]
    """Description of the underlying asset or basket of assets."""
    option_type: Optional[OptionType]
    """If the derivative instrument is an option, whether it is a call or a put or whether it cannot be determined
    whether it is a call or a put at the time of execution."""
    strike_price: Optional[StrikePrice]
    """Predetermined price at which the holder will have to buy or sell the underlying instrument, or an indication that
    the price cannot be determined at the time of execution."""
    option_exercise_style: Optional[OptionExerciseStyle]
    """Indication of whether the option may be exercised only at a fixed date (European and Asian style), a series of
    pre-specified dates (Bermudan) or at any time during the life of the contract (American style)."""
    delivery_type: Optional[DeliveryType]
    """Whether the financial instrument is cash settled or physically settled or delivery type cannot be determined at
    time of execution."""
    commodity_attributes: Optional[CommodityDerivativeAttributes]
    """If the instrument is a commodity derivative, certain commodity-related attributes."""
    ir_attributes: Optional[InterestRateDerivativeAttributes]
    """If the instrument is an interest rate derivative, certain IR-related attributes."""
    fx_attributes: Optional[FxDerivativeAttributes]
    """If the instrument is a foreign exchange derivative, certain FX-related attributes."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "DerivativeAttributes":
        """Parse a `DerivInstrmAttrbts` XML element from FIRDS into a :class:`DerivativeAttributes` object.

        :param elem: The XML element to parse, as a :class:`etree._Element` object.
        """
        # TODO: Continue refactor
        nsmap = elem.nsmap
        return DerivativeAttributes(
            expiry_date=parse_date(elem.find("XpryDt", nsmap), optional=True),
            price_multiplier=text_or_none(elem.find("PricMltplr", nsmap), wrapper=float),
            # Will probably need single "Underlying" class
            underlying=optional(elem.find("UndrlygInstrm", nsmap), DerivativeUnderlying),
            option_type=text_or_none(elem.find("OptnTp", nsmap), wrapper=OptionType),
            strike_price=optional(elem.find("StrkPric", nsmap), StrikePrice),
            option_exercise_style=text_or_none(elem.find("OptnExrcStyle", nsmap),
                                               wrapper=OptionExerciseStyle),
            delivery_type=text_or_none(elem.find("DlvryTp", nsmap), wrapper=DeliveryType),
            commodity_attributes=optional(
                elem.find("AsstClssSpcfcAttrbts/Cmmdty", nsmap),
                CommodityDerivativeAttributes
            ),
            ir_attributes=optional(
                elem.find("AsstClssSpcfcAttrbts/Intrst", nsmap),
                InterestRateDerivativeAttributes
            ),
            fx_attributes=optional(
                elem.find("AsstClssSpcfcAttrbts/Fx", nsmap),
                FxDerivativeAttributes
            )
        )


@dataclass(slots=True)
class ReferenceData(XmlParsed):
    """A base class for financial instrument reference data.
    """

    isin: str  # TODO: ISIN class?
    """The International Securities Indentifier Number (ISO 6166) of the financial instrument."""
    full_name: str
    """The full name of the financial instrument. This should give a good indication of the issuer and the particulars
    of the instrument."""
    cfi: str  # TODO: CFI class? https://en.wikipedia.org/wiki/ISO_10962
    """The Classification of Financial Instruments code (ISO 10962) of the financial instrument."""
    is_commodities_derivative: bool
    """Whether the financial instrument falls within the definition of a "commodities derivative" under
    Article 2(1)(30) of Regulation (EU) No 600/2014."""
    issuer_lei: str  # TODO: LEI class?
    """The Legal Entity identifier (ISO 17442) for the issuer. In certain cases, eg derivative instruments issued by the
    trading venue, this field will be populated with the trading venue operator's LEI."""
    fisn: str  # TODO: FISN class? https://www.iso.org/obp/ui/#iso:std:iso:18774:ed-1:v1:en
    """The Financial Instrument Short Name (ISO 18774) for the financial instrument."""
    trading_venue_attrs: TradingVenueAttributes
    """Data relating to the trading or admission to trading of the financial instrument on a trading venue."""
    notional_currency: str  # TODO: currency code class? https://en.wikipedia.org/wiki/ISO_4217
    """The currency in which the notional is denominated. For an interest rate or currency derivative contract, this
    will be the notional currency of leg 1, or the currency 1, of the pair. In the case of swaptions where the
    underlying swap is single currency, this will be the notional currency of the underlying swap. For swaptions where
    the underlying is multi-currency, this will be the notional currency of leg 1 of the swap."""
    technical_attributes: Optional[TechnicalAttributes]
    """Technical attributes of the financial instrument."""
    debt_attributes: Optional[DebtAttributes]
    """If the instrument is a debt instrument, certain debt-related attributes."""
    derivative_attributes: Optional[DerivativeAttributes]
    """If the instrument is a derivative, certain derivative-related attributes."""

    @property
    def unique_id(self) -> str:
        """A unique ID for the financial instrument reference data, consisting of its ISIN plus the MIC of the relevant
        trading venue (as the same ISIN can be reported by multiple trading venues). This identifier is not separately
        provided by the FIRDS data, but is generated from the `isin` and `trading_venue_attrs.trading_venue` attributes
        of the :class:`ReferenceData` object, which are taken from the FIRDS data. The combination of ISIN and MIC is,
        however, apparently used by ESMA to identify records uniquely.
        """
        return self.isin + self.technical_attributes.relevant_trading_venue

    @classmethod
    def from_xml(cls, elem: etree.Element) -> "ReferenceData":
        """Parse a `RefData` XML element from FIRDS into a :class:`ReferenceData` object (or appropriate subclass).

        :param elem: The XML element to parse. The tag should be
            `{urn:iso:std:iso:20022:tech:xsd:auth.017.001.02}RefData` or an equivalent XML element which belongs to the
            `document` namespace in `nsmap`.
        """
        nsmap = elem.nsmap
        gen_attrs = elem.find("FinInstrmGnlAttrbts", nsmap)
        return cls(
            isin=gen_attrs.find("Id", nsmap).text,
            full_name=gen_attrs.find("FullNm", nsmap).text,
            cfi=gen_attrs.find("ClssfctnTp", nsmap).text,
            is_commodities_derivative=parse_bool(gen_attrs.find("CmmdtyDerivInd", nsmap)),
            issuer_lei=elem.find("Issr", nsmap).text,
            fisn=gen_attrs.find("ShrtNm", nsmap).text,
            trading_venue_attrs=TradingVenueAttributes.from_xml(elem.find("TradgVnRltdAttrbts", nsmap)),
            notional_currency=gen_attrs.find("NtnlCcy", nsmap).text,
            technical_attributes=TechnicalAttributes.from_xml(elem.find("TechAttrbts", nsmap)),
            debt_attributes=optional(elem.find("DebtInstrmAttrbts", nsmap), DebtAttributes),
            derivative_attributes=optional(elem.find("DerivInstrmAttrbts", nsmap), DerivativeAttributes)
        )


@dataclass
class NewRecord(ReferenceData):
    """Reference data for a newly added financial instrument. Supports all the same properties and methods as
    :class:`ReferenceData`."""
    pass


@dataclass
class ModifiedRecord(ReferenceData):
    """Modified reference data for a financial instrument. Supports all the same properties and methods as
    :class:`ReferenceData`."""
    pass


@dataclass
class TerminatedRecord(ReferenceData):
    """Reference data for a financial instrument that has ceased being traded on a trading venue. Supports all the same
    properties and methods as :class:`ReferenceData`."""
    pass
