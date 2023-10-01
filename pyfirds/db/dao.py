import logging
from abc import ABC, abstractmethod
from typing import Any, Callable

from sqlalchemy import Engine, insert, select, Connection

from pyfirds.db.schema import publication_period, technical_attributes, index_term
from pyfirds.model import ReferenceData, PublicationPeriod, TechnicalAttributes, IndexTerm, Index

logger = logging.getLogger(__name__)


_add_data_method = Callable[["AbstractFirdsDao", Any, Connection], int]
def unique(method: _add_data_method) -> _add_data_method:
    """Wrap a method of :class:`FirdsDao` used to add data to the database"""
    def f(self, data, conn):

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

    # TODO: Make check for existing index/term and return ID if present
    def _add_index_term(self, data: IndexTerm, conn: Connection) -> int:
        """Add an :class:`IndexTerm` to the database and return its id."""
        stmt = insert(index_term).values(
            number=data.number,
            unit=data.unit
        )
        return conn.execute(stmt).inserted_primary_key[0]

    def _add_index(self, data: Index, conn: Connection) -> int:
        """Add an :class:`Index` to the database and return its id."""
        stmt = insert(index_term).values(
            name=data.name,
            isin=data.isin,
            term_id=self._add_index_term()
        )
        return conn.execute(stmt).inserted_primary_key[0]