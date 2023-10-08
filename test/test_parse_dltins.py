import os
from typing import Iterable, Callable, Type

from lxml import etree

from pyfirds.model import ReferenceData, NewRecord, ModifiedRecord, TerminatedRecord
from pyfirds.xml import X, iterparse
from test.common import TEST_DATA_DIR, FIRDS_DIR, verify_types

FIRDS_DATA = os.path.join(TEST_DATA_DIR, "firds_data")

files = os.listdir(FIRDS_DATA)


#def non_iter_parse_files(file_names: Iterable[str], parse_func: Callable[[etree.Element], list[etree.Element]],
#                         parent_name: str):
#    """Parse all files whose names start with `fname_filter`. Test that they can be properly parse into dataclass
#    objects and perform some basic checks that the results look correct.
#    """
#    for fname in file_names:
#        print(fname)
#        tree = etree.parse(os.path.join(FIRDS_DIR, fname))
#        root = tree.getroot()
#        ref_data = parse_func(root)
#        for elem in ref_data:
#            r = parse_ref_data(elem)
#            verify_types(r, ReferenceData, parent_name)


def iter_parse_files(file_names: Iterable[str], tag_name: str, cls: Type[X], parent_name: str):
    for f in file_names:
        print(f)
        for obj in iterparse(os.path.join(FIRDS_DIR, f), {tag_name: cls}):
            verify_types(obj, cls, parent_name)


delta_files = list(filter(lambda f: f.startswith('DLTINS'), files))


def test_01_parse_new_records():
    """Test parsing new record delta data."""
    iter_parse_files(delta_files, "NewRcrd", NewRecord, "new_record")


def test_02_parse_modified_records():
    """Test parsing modified record delta data."""
    iter_parse_files(delta_files, "ModfdRcrd", ModifiedRecord, "modified_record")


def test_03_parse_terminated_records():
    """Test parsing terminated record delta data."""
    #non_iter_parse_files(delta_files, get_terminated_records, "terminated_record")
    iter_parse_files(delta_files, "TermntdRcrd", TerminatedRecord, "terminated_record")
