from lxml import etree

NSMAP = {
    "biz_data": "urn:iso:std:iso:20022:tech:xsd:head.003.001.01",
    "app_hdr": "urn:iso:std:iso:20022:tech:xsd:head.001.001.01",
    "document": "urn:iso:std:iso:20022:tech:xsd:auth.017.001.02"
}

def get_ref_data(root: etree.Element) -> list[etree.Element]:
    return root.findall('biz_data:Pyld/document:Document/document:FinInstrmRptgRefDataRpt/document:RefData', NSMAP)
