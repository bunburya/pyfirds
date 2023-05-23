import os
from typing import Iterable, Callable

from lxml import etree

from pyfirds.model import ReferenceData
from pyfirds.parse.delta import get_new_records, get_modified_records, get_terminated_records
from pyfirds.parse.full import parse_ref_data
from test.common import TEST_DATA_DIR, FIRDS_DIR, verify_types

FIRDS_DATA = os.path.join(TEST_DATA_DIR, "firds_data")

files = os.listdir(FIRDS_DATA)


def parse_files(file_names: Iterable[str], parse_func: Callable[[etree.Element], list[etree.Element]],
                parent_name: str):
    """Parse all files whose names start with `fname_filter`. Test that they can be properly parse into dataclass
    objects and perform some basic checks that the results look correct.
    """
    for fname in file_names:
        print(fname)
        tree = etree.parse(os.path.join(FIRDS_DIR, fname))
        root = tree.getroot()
        ref_data = parse_func(root)
        for elem in ref_data:
            r = parse_ref_data(elem)
            verify_types(r, ReferenceData, parent_name)

delta_files = list(filter(lambda f: f.startswith('DLTINS'), files))


def test_01_parse_new_records():
    """Test parsing new record delta data."""
    parse_files(delta_files, get_new_records, "new_record")


def test_02_parse_modified_records():
    """Test parsing modified record delta data."""
    parse_files(delta_files, get_modified_records, "modified_record")


def test_03_parse_terminaeted_records():
    """Test parsing terminated record delta data."""
    parse_files(delta_files, get_terminated_records, "terminated_record")
