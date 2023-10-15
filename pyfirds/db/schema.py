from sqlalchemy import Table, MetaData, Column, String, Boolean, DateTime, Integer, ForeignKey, Float, Date, \
    UniqueConstraint

from typing import TYPE_CHECKING

# TODO: Need to think about structure of database.
# Reference data is unique by a combination of ISIN, MIC and ValidTo. ValidTo could be NULL so cannot form part of
# composite primary key. One possible solution is to have a separate table for validity period (with nullable "valid_to"
# column) and have "validity_period" column in reference_data table point to that table.

metadata = MetaData()

publication_period = Table(
    "publication_period",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("from_date", Date, nullable=False),
    Column("to_date", Date)
)

technical_attributes = Table(
    "technical_attributes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("relevant_competent_authority", String(2), nullable=False),
    Column("publication_period_id", Integer, ForeignKey("publication_period.id")),
    Column("relevant_trading_venue", String(4), nullable=False)
)

index_term = Table(
    "index_term",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("number", Integer, nullable=False),
    Column("unit", String, nullable=False),
    UniqueConstraint("number", "unit")
)

index = Table(
    "index",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("isin", String(12)),
    Column("term_id", Integer, ForeignKey("index_term.id")),
    UniqueConstraint("name", "isin", "term_id")
)

interest_rate = Table(
    "interest_rate",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("fixed_rate", Float),
    Column("benchmark_id", Integer, ForeignKey("index.id")),
    Column("spread", Integer),
    UniqueConstraint("fixed_rate", "benchmark_id", "spread")
)


strike_price = Table(
    "strike_price",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String(14)),
    Column("price", Float),
    Column("pending", Boolean, nullable=False),
    Column("currency", String(3))
)

underlying_single = Table(
    "underlying_single",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("isin", String(12)),
    Column("index_id", Integer, ForeignKey("index.id")),
    Column("issuer_lei", String(20))
)

underlying_basket = Table(
    "underlying_basket",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("isin", String),
    Column("index_id", Integer, ForeignKey("index.id")),
    Column("issuer_lei", String)
)

debt_attributes = Table(
    "debt_attributes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("total_issued_amount", Float, nullable=False),
    Column("maturity_date", Date),
    Column("nominal_currency", String(3), nullable=False),
    Column("nominal_value_per_unit", Float, nullable=False),
    Column("interest_rate_id", Integer, ForeignKey("interest_rate.id")),
    Column("seniority", String(4))
)

commodity_derivative_attributes = Table(
    "commodity_derivative_attributes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("base_product", String(4), nullable=False),
    Column("sub_product", String(4)),
    Column("further_sub_product", String(4)),
    Column("transaction_type", String(4)),
    Column("final_price_type", String(4))
)

ir_derivative_attributes = Table(
    "ir_derivative_attributes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("reference_rate_id", Integer, ForeignKey("index.id"), nullable=False),
    Column("notional_currency_2", String(3)),
    Column("fixed_rate_1", Float),
    Column("fixed_rate_2", Float),
    Column("floating_rate_2_id", Integer, ForeignKey("index.id"))
)

fx_derivative_attributes = Table(
    "fx_derivative_attributes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("notional_currency_2", String(3), nullable=False),
    Column("fx_type", String(4), nullable=False)
)

derivative_attributes = Table(
    "derivative_attributes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("expiry_date", DateTime),
    Column("price_multiplier", Float),
    Column("underlying_single_id", Integer, ForeignKey("underlying_single.id")),
    Column("underlying_basket_id", Integer, ForeignKey("underlying_basket.id")),
    Column("option_type", String(4)),
    Column("strike_price_id", Integer, ForeignKey("strike_price.id")),
    Column("option_exercise_style", String(4)),
    Column("delivery_type", String(4)),
    Column("commodity_derivative_attributes_id", Integer, ForeignKey("commodity_derivative_attributes.id")),
    Column("ir_derivative_attributes_id", Integer, ForeignKey("ir_derivative_attributes.id")),
    Column("fx_derivative_attributes_id", Integer, ForeignKey("fx_derivative_attributes.id"))
)

reference_data = Table(
    "reference_data",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("isin", String(12), nullable=False),
    Column("full_name", String(350), nullable=False),
    Column("cfi", String(6), nullable=False),
    Column("is_commodities_derivative", Boolean, nullable=False),
    Column("issuer_lei", String(20), nullable=False),
    Column("fisn", String(15), nullable=False),
    Column("tv_trading_venue", String(4), nullable=False),
    Column("tv_requested_admission", Boolean, nullable=False),
    Column("tv_approval_date", DateTime),
    Column("tv_request_date", DateTime),
    Column("tv_admission_or_first_trade_date", DateTime),
    Column("tv_termination_date", DateTime),
    Column("notional_currency", String(3), nullable=False),
    Column("technical_attributes_id", Integer, ForeignKey("technical_attributes.id")),
    Column("debt_attributes_id", Integer, ForeignKey("debt_attributes.id")),
    Column("derivative_attributes_id", Integer, ForeignKey("derivative_attributes.id")),
    Column("valid_from", Date, nullable=False),
    Column("valid_to", Date),
    UniqueConstraint("isin", "tv_trading_venue", "valid_to")
)