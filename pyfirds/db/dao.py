import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from sqlalchemy import Engine, insert, select, Connection, Column, Table

from pyfirds.db.schema import publication_period, technical_attributes, index_term, index, interest_rate, \
    debt_attributes, strike_price, commodity_derivative_attributes, ir_derivative_attributes
from pyfirds.model import ReferenceData, PublicationPeriod, TechnicalAttributes, IndexTerm, Index, InterestRate, \
    DebtAttributes, StrikePrice, CommodityDerivativeAttributes, InterestRateDerivativeAttributes

logger = logging.getLogger(__name__)


class AbstractFirdsDao(ABC):

    def __init__(self, engine: Engine):
        self.engine = engine

    @abstractmethod
    def add_reference_data(self, data: ReferenceData, commit: bool = False) -> int:
        """Add reference data for a financial instrument to the database.

        :param data: The data to add to the database.
        :param commit: Whether to commit the data to the database immediately after adding.
        :return: The primary key (rowid) of the added row in the database.
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, *args, **kwargs) -> list[ReferenceData]:
        """Search the database for reference data matching the provided query parameters and return a list of matching
        :class:`ReferenceData` objects.
        """
        raise NotImplementedError


class FirdsDao(AbstractFirdsDao):

    def add_reference_data(self, data: ReferenceData, commit: bool = False) -> int:
        raise NotImplementedError

    def _add_publication_period(self, data: PublicationPeriod, conn: Connection) -> int:
        """Add a :class:`PublicationPeriod` to the database and return its id."""
        stmt = insert(publication_period).values(from_date=data.from_date, to_date=data.to_date)
        return conn.execute(stmt).inserted_primary_key[0]

    def _add_tech_attrs(self, data: TechnicalAttributes, conn: Connection) -> int:
        """Add :class:`TechnicalAttributes` to the database and return its id."""
        stmt = insert(technical_attributes).values(
            relevant_competent_authority=data.relevant_competent_authority,
            publication_period_id=self._add_publication_period(data.publication_period, conn),
            relevant_trading_venue=data.relevant_trading_venue
        )
        return conn.execute(stmt).inserted_primary_key[0]

    def _search_ids(self, table: Table, match: dict[str, Any], conn: Connection) -> list[int]:
        """Search for all rows matching certain criteria.

        :param table: The table to search.
        :param match: A dict mapping column names to values to match against.
        :return: A list of row IDs for matching rows.
        """
        stmt = select(table).filter_by(**match)
        results = conn.execute(stmt).all()
        return [r.id for r in results]

    def _search_id(self, table: Table, match: dict[str, Any], conn: Connection) -> Optional[int]:
        """Like `_search_ids`, but only returns the row id for the first matching row, or None if no matching row is
        found.
        """
        ids = self._search_ids(table, match, conn)
        if not ids:
            return None
        if (c := len(ids)) > 1:
            logger.warning(f"Found {c} matching rows in table `{table}` for query `{match}`.")
        return ids[0]

    def _add_index_term(self, data: IndexTerm, conn: Connection) -> int:
        """Add an :class:`IndexTerm` to the database (if not already present) and return the row id."""
        existing = self._search_id(index_term, {"number": data.number, "unit": data.unit}, conn)
        if existing is not None:
            return existing
        stmt = insert(index_term).values(
            number=data.number,
            unit=data.unit
        )
        return conn.execute(stmt).inserted_primary_key[0]

    def _add_index(self, data: Index, conn: Connection) -> int:
        """Add an :class:`Index` to the database (if not already present) and return the row id."""
        existing_term_id = self._search_id(index_term, {"number": data.term.number, "unit": data.term.unit}, conn)
        existing = self._search_id(index, {"name": data.name, "isin": data.isin, "term_id": existing_term_id}, conn)
        if existing is not None:
            return existing

        # If we found an existing ID for the term above, reuse it rather than searching again
        if existing_term_id is not None:
            term_id = existing_term_id
        else:
            term_id = self._add_index_term(data.term, conn)

        stmt = insert(index).values(
            name=data.name,
            isin=data.isin,
            term_id=term_id
        )
        return conn.execute(stmt).inserted_primary_key[0]

    def _add_interest_rate(self, data: InterestRate, conn: Connection) -> int:
        """Add an :class:`InterestRate` to the database (if not already present) and return the row id."""
        existing_benchmark_id = self._search_id(
            index,
            {
                "name": data.benchmark.name,
                "isin": data.benchmark.isin,
                "term_id": self._search_id(
                    index_term,
                    {"number": data.benchmark.term.number, "unit": data.benchmark.term.unit},
                    conn
                )
            },
            conn
        )
        existing = self._search_id(
            interest_rate,
            {
                "fixed_rate": data.fixed_rate,
                "benchmark_id": existing_benchmark_id,
                "spread": data.spread
            },
            conn
        )
        if existing is not None:
            return existing

        # If we found an existing ID for the benchmark above, reuse it rather than searching again
        if existing_benchmark_id is not None:
            benchmark_id = existing_benchmark_id
        else:
            benchmark_id = self._add_index(data.benchmark, conn)

        stmt = insert(index).values(
            fixed_rate=data.fixed_rate,
            benchmark_id=benchmark_id,
            spread=data.spread
        )
        return conn.execute(stmt).inserted_primary_key[0]

    def _add_debt_attrs(self, data: DebtAttributes, conn: Connection) -> int:
        """Add :class:`DebtAttributes` to the database and return the row id."""
        stmt = insert(debt_attributes).values(
            total_issued_amount=data.total_issued_amount,
            maturity_date=data.maturity_date,
            nominal_currency=data.nominal_currency,
            nominal_value_per_unit=data.nominal_value_per_unit,
            interest_rate_id=self._add_interest_rate(data.interest_rate, conn),
            seniority=data.seniority
        )
        return conn.execute(stmt).inserted_primary_key[0]

    def _add_strike_price(self, data: StrikePrice, conn: Connection) -> int:
        """Add :class:`StrikePrice` to the database and return the row id."""

        stmt = insert(strike_price).values(
            type=data.price_type,
            price=data.price,
            pending=data.pending,
            currency=data.currency
        )
        return conn.execute(stmt).inserted_primary_key[0]

    def _add_commodity_deriv_attrs(self, data: CommodityDerivativeAttributes, conn: Connection) -> int:
        """Add :class:`CommodityDerivativeAttributes` to the database and return the row id."""

        stmt = insert(commodity_derivative_attributes).values(
            base_product=data.base_product,
            sub_product=data.sub_product,
            transaction_type=data.transaction_type,
            final_price_type=data.final_price_type
        )
        return conn.execute(stmt).inserted_primary_key[0]

    def _add_ir_deriv_attrs(self, data: InterestRateDerivativeAttributes, conn: Connection) -> int:
        """Add :class:`InterestRateDerivativeAttributes` to the database and return the row id."""

        stmt = insert(ir_derivative_attributes).values(
            reference_rate_id=self._add_index(data.reference_rate, conn),
            notional_currency_2=data.notional_currency_2,
            fixed_rate_1=data.fixed_rate_1,
            fixed_rate_2=data.fixed_rate_2,
            floating_rate_2_id=self._add_index(data.floating_rate_2, conn)
        )
        return conn.execute(stmt).inserted_primary_key[0]


"""    Column("reference_rate_id", Integer, ForeignKey("index.id"), nullable=False),
    Column("notional_currency_2", String(3)),
    Column("fixed_rate_1", Float),
    Column("fixed_rate_2", Float),
    Column("floating_rate_2_id", Integer, ForeignKey("index.id"))
"""