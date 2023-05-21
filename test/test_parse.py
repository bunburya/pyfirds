import os
from dataclasses import fields
from typing import Type, Any

from lxml import etree

from pyfirds.model import ReferenceData
from pyfirds.parse import get_ref_data, parse_ref_data
from test.values import TEST_DATA_DIR

FIRDS_DATA = os.path.join(TEST_DATA_DIR, "firds_data")

files = os.listdir(FIRDS_DATA)

def verify_types(val: Any, type_: Type, name: str):
    """
    :param val: Value to check against `type_`.
    :param type_: Expected type of `val`.
    :param name: The variable name of `val`.
    """
    assert isinstance(val, type_), f"{name} should be {type_} but is {val}"
    try:
        for f in fields(val):
            verify_types(getattr(val, f.name), f.type, f"{name}.{f.name}")
    except TypeError:
        pass

def _parse_files(fname_filter: str):
    """Parse all files whose names start with `fname_filter`. Test that they can be properly parse into dataclass
    objects and perform some basic checks that the results look correct.
    """
    for fname in filter(lambda f: f.startswith(fname_filter), files):
        print(fname)
        tree = etree.parse(os.path.join(FIRDS_DATA, fname))
        root = tree.getroot()
        ref_data = get_ref_data(root)
        for elem in ref_data:
            r = parse_ref_data(elem)
            verify_types(r, ReferenceData, 'ref_data')

def test_01_fulins_c():
    """Test parsing full collective investment scheme instrument reference data."""
    _parse_files('FULINS_C')

def test_02_fulins_d():
    """Test parsing full debt instrument reference data."""
    _parse_files('FULINS_D')

def test_03_fulins_e():
    """Test parsing full equity instrument reference data."""
    _parse_files('FULINS_E')

def test_04_fulins_f():
    """Test parsing full futures instrument reference data."""
    _parse_files('FULINS_F')

def test_05_fulins_h():
    """Test parsing full non-listed and complex options instrument reference data."""
    _parse_files('FULINS_H')

def test_06_fulins_i():
    """Test parsing full spot instrument reference data."""
    _parse_files('FULINS_I')

def test_07_fulins_j():
    """Test parsing full forwards instrument reference data."""
    _parse_files('FULINS_J')

def test_08_fulins_o():
    """Test parsing full listed options instrument reference data."""
    _parse_files('FULINS_O')

def test_09_fulins_r():
    """Test parsing full entitlement instrument reference data."""
    _parse_files('FULINS_R')

def test_10_fulins_s():
    """Test parsing full swap instrument reference data."""
    _parse_files('FULINS_S')
