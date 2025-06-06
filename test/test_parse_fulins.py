import os
from typing import Iterable

from pyfirds.model import ReferenceData
from pyfirds.xml_utils import iterparse
from test.common import ESMA_FIRDS_FILES, verify_types, ESMA_FIRDS_DIR, FCA_FIRDS_DIR, FCA_FIRDS_FILES


#def non_iter_parse_files(file_names: Iterable[str], parent_name: str):
#    """Parse all files whose names start with `fname_filter`. Test that they can be properly parse into dataclass
#    objects and perform some basic checks that the results look correct.
#    """
#    for fname in file_names:
#        print(fname)
#        tree = etree.parse(os.path.join(FIRDS_DIR, fname))
#        root = tree.getroot()
#        ref_data = get_ref_data_elems(root)
#        for elem in ref_data:
#            r = ReferenceData.from_xml(elem)
#            verify_types(r, ReferenceData, parent_name)


def iter_parse_files(firds_dir: str, file_names: Iterable[str], parent_name: str):
    for f in file_names:
        print(f)
        for ref_data in iterparse(os.path.join(firds_dir, f), {"RefData": ReferenceData}):
            verify_types(ref_data, ReferenceData, parent_name)


def test_01_fulins_c():
    """Test parsing full collective investment scheme instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_C"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_C"), FCA_FIRDS_FILES), "ref_data")

def test_02_fulins_d():
    """Test parsing full debt instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_D"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_D"), FCA_FIRDS_FILES), "ref_data")

def test_03_fulins_e():
    """Test parsing full equity instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_E"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_E"), FCA_FIRDS_FILES), "ref_data")


def test_04_fulins_f():
    """Test parsing full futures instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_F"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_F"), FCA_FIRDS_FILES), "ref_data")


def test_05_fulins_h():
    """Test parsing full non-listed and complex options instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_H"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_H"), FCA_FIRDS_FILES), "ref_data")


def test_06_fulins_i():
    """Test parsing full spot instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_I"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_I"), FCA_FIRDS_FILES), "ref_data")


def test_07_fulins_j():
    """Test parsing full forwards instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_J"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_J"), FCA_FIRDS_FILES), "ref_data")


def test_08_fulins_o():
    """Test parsing full listed options instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_O"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_O"), FCA_FIRDS_FILES), "ref_data")


esma_r_files = list(filter(lambda f: f.startswith("FULINS_C"), ESMA_FIRDS_FILES))
fca_r_files = list(filter(lambda f: f.startswith("FULINS_C"), FCA_FIRDS_FILES))


def test_09_fulins_r_1():
    """Test parsing full entitlement instrument reference data. (1 of 2)"""
    iter_parse_files(ESMA_FIRDS_DIR, esma_r_files[:len(esma_r_files) // 2], "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, fca_r_files[:len(fca_r_files) // 2], "ref_data")


def test_10_fulins_r_2():
    """Test parsing full entitlement instrument reference data. (2 of 2)"""
    iter_parse_files(ESMA_FIRDS_DIR, esma_r_files[len(esma_r_files) // 2:], "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, fca_r_files[len(fca_r_files) // 2:], "ref_data")


def test_11_fulins_s():
    """Test parsing full swap instrument reference data."""
    iter_parse_files(ESMA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_S"), ESMA_FIRDS_FILES), "ref_data")
    iter_parse_files(FCA_FIRDS_DIR, filter(lambda f: f.startswith("FULINS_S"), FCA_FIRDS_FILES), "ref_data")
