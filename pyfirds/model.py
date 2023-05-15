from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Optional, Union, Any

from pyfirds.categories import DebtSeniority, OptionType, OptionExerciseStyle, DeliveryType, BaseProduct, SubProduct, \
    FurtherSubProduct, IndexTermUnit, TransactionType, FinalPriceType, FxType, IndexName


@dataclass
class IndexTerm:
    """The term of an index or benchmark.

    :param number: The number of weeks, months, etc (as determined by `unit`).
    :param unit: The unit of time in which the term is expressed (days, weeks, months or years).
    """

    number: int
    unit: IndexTermUnit

@dataclass
class StrikePrice:
    """The strike price of a derivative instrument.

    The different optional attributes are different ways in which the price may be expressed.  At most one of them
    should be specified.

    :param monetary_value: The price expressed as a monetary value.
    :param percentage: The price expressed as a percentage.
    :param yield_: The price expressed as a yield.
    :param basis_points: The price expressed as basis points.
    :param pending: Whether the price is currently not available and is pending.
    :param currency: The currency in which the price is denominated.
    """

    monetary_value: Optional[float]
    percentage: Optional[float]
    yield_: Optional[float]
    basis_points: Optional[float]
    pending: bool
    currency: Optional[str]

@dataclass
class Index:
    """An index or benchmark rate that is used in the reference data for certain financial instruments.

    :param name: The name of the index or benchmark. Should either be a :class:`IndexName` object or a 25 character
        string.
    :param isin: The ISIN of the index or benchmark.
    :param term: The term of the index or benchmark.


    """
    name: Optional[Union[str, IndexName]]
    isin: Optional[str]
    term: Optional[IndexTerm]

@dataclass
class TradingVenueAttributes:
    """Data relating to the trading or admission to trading of a financial instrument on a trading venue.

    :param trading_venue: The Market Identifier Code (ISO 20022) for the trading venue or systemic internaliser. A
        segment MIC is used where available; otherwise, an operating MIC is used.
    :param requested_admission: Whether the issuer has requested or approved the trading or admission to trading of their
        financial instruments on a trading venue.
    :param approval_date: Date and time the issuer has approved admission to trading or trading in its financial
        instruments on a trading venue.
    :param request_date: Date and time of the request for admission to trading on the trading venue.
    :param admission_or_first_trade_date: Date and time of the admission to trading on the trading venue or the date and
        time when the instrument was first traded or an order or quote was first received by the trading venue.
    :param termination_date: Date and time when the instrument ceases to be traded or admitted to trading on the trading
        venue.

    """

    trading_venue: str  # TODO: MIC class? https://www.iso20022.org/market-identifier-codes
    requested_admission: bool
    approval_date: Optional[datetime]
    request_date: Optional[datetime]
    admission_or_first_trade_date: Optional[datetime]
    termination_date: Optional[datetime]


@dataclass
class InterestRate:
    """Data about the interest rate applicable to a debt instrument.

    :param fixed_rate: The interest rate payable on a fixed rate instrument, expressed as a percentage (eg, 7.5 means
        7.5% interest rate).
    :param benchmark: The benchmark or index of a floating rate instrument.
    :param spread: Spread of a floating rate instrument, expressed as an integer number of basis points.
    """

    fixed_rate: Optional[float]
    benchmark: Optional[Index]
    spread: Optional[int]

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

@dataclass
class PublicationPeriod:
    """The period for which details on a financial instrument were published.

    :param from_date: The date from which details on the financial instrument were published.
    :param to_date: The date to which details on the financial instrument were published.
    """

    from_date: date
    to_date: Optional[date]

@dataclass
class TechnicalAttributes:
    """The technical attributes of a financial instrument (ie, attributes relating to the submission of details of the
    financial instrument to FIRDS).

    :param is_inconsistent: Whether the record has been flagged by FIRDS as inconsistent.
    :param last_update: The date and time when this financial instrument was last received by FIRDS.
    :param submission_date_time: The date and time when this instrument was originally received by at the submission
        destination. Used by Competent Authorities to indicate the date and time they received the record from the
        corresponding TV/SI. Only populated where a competent authority has aggregated a number of reports for
        transmission to ESMA and details on the reference data report are different across the originally received
        reports.
    :param relevant_competent_authority: The relevant competent authority for the instrument.
    :param publication_period: The period for which these details on the financial instrument was published.
    :param never_published: Whether the instrument was only reported after their termination date and never published
        on the reference data files.
    """
    is_inconsistent: bool
    last_update: datetime
    submission_date_time: Optional[datetime]
    relevant_competent_authority: str
    publication_period: PublicationPeriod
    never_published: bool

# TODO: Rather than inheritance, have DebtInstrumentAttributes, DerivativeInstrumentAttributes etc as optional
#  properties of ReferenceData. That way each one can be parsed from the relevant sub-element of RefData, and we can
#  tell what type of instrument is being referred to by checking for the presence of the relevant attributes.

@dataclass
class DebtAttributes:
    """Reference data for bonds or other forms of securitised debt.

    :param total_issued_amount: The total issued nominal amount of the financial instrument. Amount is expressed in the
        `nominal_currency`.
    :param maturity_date: The maturity date of the financial instrument. Only applies to debt instruments with defined
        maturity.
    :param nominal_currency: The currency of the nominal value.
    :param nominal_value_per_unit: The nominal value of each traded unit. If not available, the minimum traded amount is
        included. Amount is expressed in the `nominal_currency`.
    :param interest_rate: Details of the interest rate applicable to the financial instrument.
    :param seniority: The seniority of the financial instrument (senior, mezzanine, subordinated or junior).
    """
    total_issued_amount: float
    maturity_date: Optional[datetime]
    nominal_currency: str
    nominal_value_per_unit: float
    interest_rate: InterestRate
    seniority: DebtSeniority

@dataclass
class CommodityDerivativeAttributes:
    """Additional reference data for a commodity derivative instrument.

    :param base_product: The base product for the underlying asset class.
    :param sub_product: The sub-product for the underlying asset class.
    :param further_sub_product: The further sub-product (ie, sub-sub-product) for the underlying asset class.
    :param transaction_type: The transaction type as specified by the trading venue.
    :param final_price_type: The final price type as specified by the trading venue.
    """
    base_product: BaseProduct
    sub_product: Optional[SubProduct]
    further_sub_product: Optional[FurtherSubProduct]
    transaction_type: TransactionType
    final_price_type: FinalPriceType

@dataclass
class InterestRateDerivativeAttributes:
    """Additional reference data for an interest rate derivative instrument.

    :param reference_rate: The reference rate.
    :param notional_currency_2: In the case of multi-currency or cross-currency swaps the currency in which leg 2 of the
        contract is denominated. For swaptions where the underlying swap is multi-currency, the currency in which leg 2
        of the swap is denominated.
    :param fixed_rate_1: The fixed rate of leg 1 of the trade, if applicable. Expressed as a percentage.
    :param fixed_rate_2: The fixed rate of leg 2 of the trade, if applicable. Expressed as a percentage.
    :param floating_rate_2: The floating rate of leg 2 of the trade, if applicable.
    """
    reference_rate: Index
    notional_currency_2: Optional[str]
    fixed_rate_1: Optional[float]
    fixed_rate_2: Optional[float]
    floating_rate_2: Optional[Index]

@dataclass
class FxDerivativeAttributes:
    """Additional reference data for a foreign exchange derivative instrument.

    :param notional_currency_2: The second currency of the currency pair.
    :param fx_type: The type of underlying currency.
    """
    notional_currency_2: str
    fx_type: FxType

@dataclass
class DerivativeAttributes:
    """Reference data for a derivative instrument.

    :param expiry_date: Expiry date of the instrument.
    :param price_multiplier: Number of units of the underlying instrument represented by a single derivative contract.
        For a future or option on an index, the amount per index point.
    :param underlying_isins: A list of one or more ISINs of the underlying instruments.
        - For ADRs, GDRs and similar instruments, the ISIN code of the financial instrument on which those instruments
        are based. For convertible bonds, the ISIN code of the instrument in which the bond can be converted.
        - For derivatives or other instruments which have an underlying, the underlying instrument ISIN code, when the
        underlying is admitted to trading, or traded on a trading venue. Where the underlying is a stock dividend, then
        the ISIN code of the related share entitling the underlying dividend shall be provided.
        - For Credit Default Swaps, the ISIN of the reference obligation shall be provided.
    :param underlying_issuers: Where the instrument is referring to an issuer, rather than to one single instrument, the
        LEI code of the issuer.
    :param underlying_index: The underlying index of the instrument.
    :param option_type: If the derivative instrument is an option, whether it is a call or a put or whether it cannot
        be determined whether it is a call or a put at the time of execution.
    :param strike_price: Predetermined price at which the holder will have to buy or sell the underlying instrument, or
        an indication that the price cannot be determined at the time of execution.
    :param option_exercise_style: Indication of whether the option may be exercised only at a fixed date (European
        and Asian style), a series of pre-specified dates (Bermudan) or at any time during the life of the contract
        (American style).
    :param delivery_type: Whether the financial instrument is cash settled or physically settled or delivery type cannot
        be determined at time of execution.
    :param commodity_attributes: If the instrument is a commodity derivative, certain commodity-related attributes.
    :param ir_attributes: If the instrument is an interest rate derivative, certain IR-related attributes.
    :param fx_attributes: If the instrument is a foreign exchange derivative, certain FX-related attributes.
    """

    expiry_date: Optional[datetime]
    price_multiplier: float
    underlying_isins: Optional[list[str]]
    underlying_issuers: Optional[list[str]]
    underlying_index: Optional[Index]
    option_type: Optional[OptionType]
    strike_price: Optional[StrikePrice]
    option_exercise_style: OptionExerciseStyle
    delivery_type: DeliveryType
    commodity_attributes: Optional[CommodityDerivativeAttributes]
    ir_attributes: Optional[InterestRateDerivativeAttributes]
    fx_attributes: Optional[FxDerivativeAttributes]


@dataclass
class ReferenceData:
    """A base class for financial instrument reference data.

    :param isin: The International Securities Indentifier Number (ISO 6166) of the financial instrument.
    :param full_name: The full name of the financial instrument. This should give a good indication of the issuer and
        the particulars of the instrument.
    :param cfi: The Classification of Financial Instruments code (ISO 10962) of the financial instrument.
    :param is_commodities_derivative: Whether the financial instrument falls within the definition of a "commodities
        derivative" under Article 2(1)(30) of Regulation (EU) No 600/2014.
    :param issuer_lei: The Legal Entity identifier (ISO 17442) for the issuer. In certain cases, eg derivative
        instruments issued by the trading venue, this field will be populated with the trading venue operator's LEI.
    :param fisn: The Financial Instrument Short Name (ISO 18774) for the financial instrument.
    :param trading_venue_attrs: Data relating to the trading or admission to trading of the financial instrument on a
        trading venue.
    :param notional_currency: The currency in which the notional is denominated. For an interest rate or currency
        derivative contract, this will be the notional currency of leg 1, or the currency 1, of the pair. In the case
        of swaptions where the underlying swap is single currency, this will be the notional currency of the underlying
        swap. For swaptions where the underlying is multi-currency, this will be the notional currency of leg 1 of the
        swap.
    :param technical_record_id: A unique identifier used by the FIRDS error management routine to identify any error
        related to it. The reporting date followed by a sequence number (YYYYMMDDnxxxxxxx) could be used.
    :param technical_attributes: Technical attributes of the financial instrument.
    :param debt_attributes: If the instrument is a debt instrument, certain debt-related attributes.
    :param derivative_attributes: If the instrument is a derivative, certain derivative-related attributes.

    """

    isin: str  # TODO: ISIN class?
    full_name: str
    cfi: str  # TODO: CFI class? https://en.wikipedia.org/wiki/ISO_10962
    is_commodities_derivative: bool
    issuer_lei: str  # TODO: LEI class?
    fisn: str  # TODO: FISN class? https://www.iso.org/obp/ui/#iso:std:iso:18774:ed-1:v1:en
    trading_venue_attrs: TradingVenueAttributes
    notional_currency: str  # TODO: currency code class? https://en.wikipedia.org/wiki/ISO_4217
    technical_record_id: str
    technical_attributes: TechnicalAttributes
    debt_attributes: DebtAttributes
    derivative_attributes: Optional[DerivativeAttributes]


