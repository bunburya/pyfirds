from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy import Row


class BaseRowParsed(ABC):
    """A base class for objects which can be constructed from :class:`sqlalchemy.Row` objects."""

    @classmethod
    @abstractmethod
    def from_row(cls, row: Optional[Row]) -> Optional['BaseRowParsed']:
        """Create an instance of the class from  an appropriate SQL row. If provided with None rather than a row,
        simply returns None.
        """
        raise NotImplementedError
