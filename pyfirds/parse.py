from datetime import datetime
from typing import Any

from lxml import etree

NSMAP = {
    "biz_data": "urn:iso:std:iso:20022:tech:xsd:head.003.001.01",
    "app_hdr": "urn:iso:std:iso:20022:tech:xsd:head.001.001.01",
    "document": "urn:iso:std:iso:20022:tech:xsd:auth.017.001.02"
}


def get_ref_data(root: etree.Element) -> list[etree.Element]:
    return root.findall('biz_data:Pyld/document:Document/document:FinInstrmRptgRefDataRpt/document:RefData', NSMAP)

def gen_attrs_to_dict(elem: etree.Element) -> dict[str, Any]:
    """Parse a `FinInstrmGnlAttrbts` XML element and return a dict mapping attribute names to values. The attribute
    names correspond to the property names of the :class:`model.ReferenceData` dataclass.
    """
    return {
        'isin': elem.find('document:Id', NSMAP).text,
        'full_name': elem.find('document:FullNm', NSMAP).text,
        'short_name': elem.find('document:ShrtNm', NSMAP).text,
        'cfi': elem.find('document:ClssfctnTp', NSMAP).text,
        'notional_currency': elem.find('document:NtnlCcy', NSMAP).text,
        'is_commodity_derivative': elem.find('document:CmmdtyDerivInd').text.lower() == 'true'
    }

def tech_attrs_to_dict(elem: etree.Element) -> dict[str, Any]:
    """Parse a `TechAttrbts` XML element and return a dict mapping attribute names to values. The attribute
    names correspond to the property names of the :class:`model.ReferenceData` dataclass.
    """
    return {

    }


