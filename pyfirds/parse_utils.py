from enum import Enum
from typing import Optional, Union, Callable, Type, TypeVar

from lxml import etree


class BaseXmlParsed:
    """A base class for objects which are parsed from an XML element."""

    @classmethod
    def from_xml(cls, elem: etree.Element) -> 'BaseXmlParsed':
        raise NotImplementedError


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


X = TypeVar("X", bound=BaseXmlParsed)


def optional(elem: Optional[etree.Element], cls: Type[X]) -> Optional[X]:
    if elem is None:
        return None
    else:
        return cls.from_xml(elem)
