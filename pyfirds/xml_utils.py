from abc import ABC, abstractmethod
from datetime import datetime, date
from enum import Enum
from typing import Optional, Union, Callable, Type, TypeVar, Generator

from dateutil.parser import parse
from lxml import etree
from lxml.etree import QName


class XmlParsed(ABC):
    """A base class for objects which can be parsed from an XML element."""

    @classmethod
    @abstractmethod
    def from_xml(cls, elem: etree.Element) -> 'XmlParsed':
        """Create an instance of the class from an appropriate XML element."""
        raise NotImplementedError


T = TypeVar("T")
X = TypeVar("X", bound=XmlParsed)


def text_or_none(
        elem: Optional[etree.Element],
        wrapper: Optional[Union[Callable[[str], T], Type[Enum]]] = None
) -> Optional[Union[T, Enum, str]]:
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
    return parse(value)


def parse_date(elem: Optional[etree.Element], optional: bool = False) -> Optional[date]:
    """Parse a date string in the FIRDS data to a date object.

    :param elem: XML element which contains the text value to parse, in ISO 8601 date format as used in FIRDS.
    :param optional: If True and `elem` is None, return None. Useful where the data is optional in FIRDS.
    """
    if elem is None:
        if optional:
            return None
        else:
            raise ValueError(f"Received NoneType when parsing non-optional element.")
    value = elem.text.rstrip("Z")  # FCA data includes a Z at the end
    return date.fromisoformat(value)


def optional(elem: Optional[etree.Element], cls: Type[X]) -> Optional[X]:
    if elem is None:
        return None
    else:
        return cls.from_xml(elem)


def iterparse(
        file: str,
        tag_localname_to_cls: dict[str, Type[X]]
) -> Generator[X, None, dict[str, int]]:
    """Parse an XML file iteratively, creating and yielding a :class:`ReferenceData` (or subclass) object from each
    relevant node, and deleting nodes as we finish with them, to preserve memory.
    :param file: Path to the XML file to parse.
    :param tag_localname_to_cls: A dict mapping each XML tag name (after the namespace bit) to the class to be generated
        from it (which should be a subclass of :class:`BaseXmlParsed` or otherwise have an appropriate `from_xml` class
        method).
    :return: A dict specifying the number of XML elements of each given tag encountered.
    """

    tags = ["{*}" + t for t in tag_localname_to_cls]

    count = {t: 0 for t in tag_localname_to_cls}
    for evt, elem in etree.iterparse(file, tag=tags):
        localname = QName(elem).localname
        cls = tag_localname_to_cls[localname]
        obj = cls.from_xml(elem)
        elem.clear()
        for ancestor in elem.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
        count[localname] += 1
        yield obj
    return count


def ref_data(file: str) -> list[etree.Element]:
    tree = etree.parse(file)
    root = tree.getroot()
    nsmap = root.nsmap
    return root.findall("biz_data:Pyld/document:Document/document:FinInstrmRptgRefDataRpt/document:RefData")
