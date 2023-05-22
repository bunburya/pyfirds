from typing import Union

from lxml import etree

from pyfirds.model import NewRecord, ModifiedRecord, TerminatedRecord
from pyfirds.parse.full import parse_ref_data

NSMAP = {
    "biz_data": "urn:iso:std:iso:20022:tech:xsd:head.003.001.01",
    "app_hdr": "urn:iso:std:iso:20022:tech:xsd:head.001.001.01",
    "document": "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02"
}


def get_delta_data(root: Union[etree.ElementTree, etree.Element]) -> list[etree.Element]:
    """Get a list of `FinInstrmRptgRefDataDltaRpt` XML elements from the root XML element of a DLTINS XML file."""
    return root.findall("biz_data:Pyld/document:Document/document:FinInstrmRptgRefDataDltaRpt", NSMAP)


def get_modified_records(elem: etree.Element) -> list[etree.Element]:
    """Get a list of `ModfdRcrd` XML elements from a `FinInstrmRptgRefDataDltaRpt` element."""
    return elem.findall("document:FinInstrm/document:ModfdRcrd", NSMAP)


def get_new_records(elem: etree.Element) -> list[etree.Element]:
    """Get a list of `NewRcrd` XML elements from a `FinInstrmRptgRefDataDltaRpt` element."""
    return elem.findall("document:FinInstrm/document:NewRcrd", NSMAP)


def get_terminated_records(elem: etree.Element) -> list[etree.Element]:
    """Get a list of `TermntdRcrd` XML elements from a `FinInstrmRptgRefDataDltaRpt` element."""
    return elem.findall("document:FinInstrm/document:TermntdRcrd", NSMAP)


def get_cancelled_records(elem: etree.Element) -> list[etree.Element]:
    """Get a list of `CancRcrd` XML elements from a `FinInstrmRptgRefDataDltaRpt` element."""
    return elem.findall("document:FinInstrm/document:CancRcrd", NSMAP)


def parse_new_record(elem: etree.Element) -> NewRecord:
    """Parse a `NewRcrd XML element from FIRDS into a :class:`NewRecord` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.036.001.02}NewRcrd`
        or equivalent.
    """
    return parse_ref_data(elem, cls=NewRecord, nsmap=NSMAP)


def parse_modified_record(elem: etree.Element) -> ModifiedRecord:
    """Parse a `ModfdRcrd XML element from FIRDS into a :class:`ModifiedRecord` object.

    :param elem: The XML element to parse. The tag should be `{urn:iso:std:iso:20022:tech:xsd:auth.036.001.02}ModfdRcrd`
        or equivalent.
    """
    return parse_ref_data(elem, cls=ModifiedRecord, nsmap=NSMAP)


def parse_terminated_record(elem: etree.Element) -> TerminatedRecord:
    """Parse a `TermntdRcrd XML element from FIRDS into a :class:`TerminatedRecord` object.

    :param elem: The XML element to parse. The tag should be
        `{urn:iso:std:iso:20022:tech:xsd:auth.036.001.02}TermntdRcrd` or equivalent.
    """
    return parse_ref_data(elem, cls=TerminatedRecord, nsmap=NSMAP)
