import os
from typing import Iterable, Type

from pyfirds.model import NewRecord, ModifiedRecord, TerminatedRecord
from pyfirds.xml_utils import X, iterparse
from test.common import ESMA_FIRDS_FILES, verify_types, FCA_FIRDS_FILES, ESMA_FIRDS_DIR, FCA_FIRDS_DIR


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


def iter_parse_files(firds_dir: str, file_names: Iterable[str], tag_name: str, cls: Type[X], parent_name: str):
    for f in file_names:
        print(f)
        for obj in iterparse(os.path.join(firds_dir, f), {tag_name: cls}):
            verify_types(obj, cls, parent_name)


esma_delta_files = list(filter(lambda f: f.startswith('DLTINS'), ESMA_FIRDS_FILES))
fca_delta_files = list(filter(lambda f: f.startswith('DLTINS'), FCA_FIRDS_FILES))


def test_01_parse_new_records():
    """Test parsing new record delta data."""
    iter_parse_files(ESMA_FIRDS_DIR, esma_delta_files, "NewRcrd", NewRecord, "new_record")
    iter_parse_files(FCA_FIRDS_DIR, fca_delta_files, "NewRcrd", NewRecord, "new_record")


def test_02_parse_modified_records():
    """Test parsing modified record delta data."""
    iter_parse_files(ESMA_FIRDS_DIR, esma_delta_files, "ModfdRcrd", ModifiedRecord, "modified_record")
    iter_parse_files(FCA_FIRDS_DIR, fca_delta_files, "ModfdRcrd", ModifiedRecord, "modified_record")


def test_03_parse_terminated_records():
    """Test parsing terminated record delta data."""
    #non_iter_parse_files(delta_files, get_terminated_records, "terminated_record")
    iter_parse_files(ESMA_FIRDS_DIR, esma_delta_files, "TermntdRcrd", TerminatedRecord, "terminated_record")
    iter_parse_files(FCA_FIRDS_DIR, fca_delta_files, "TermntdRcrd", TerminatedRecord, "terminated_record")
