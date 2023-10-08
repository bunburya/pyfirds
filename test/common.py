import os
from dataclasses import fields
from datetime import datetime, date
from typing import Any, Type

TEST_DATA_DIR = os.path.join("test_data")
TEST_RUN_BASE_DIR = os.path.join(TEST_DATA_DIR, "run")
TEST_FIRDS_DATA_DIR = os.path.join(TEST_DATA_DIR, "firds_data")

FIRDS_DIR = os.path.join(TEST_DATA_DIR, "firds_data")
firds_files = os.listdir(FIRDS_DIR)

if not os.path.exists(TEST_RUN_BASE_DIR):
    os.makedirs(TEST_RUN_BASE_DIR)


def get_test_run_dir(name: str) -> str:
    dir_path = os.path.join(TEST_RUN_BASE_DIR, name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def verify_types(val: Any, type_: Type, name: str):
    """Verify that `val` is of type `type_`. If `val` is a dataclass, also check that its parameters are of the correct
    type (recursively).

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


def get_fulins(inst_type: str = None, file_date: date = None) -> list[str]:
    """Return FIRDS FULINS data files confirming to the specified criteria.

    :param inst_type: The type of financial instrument, as the first letter of the CFI code.
    :param file_date: Only return files from this date.
    :return: A list of file paths for the relevant data files.
    """

    def test(fname: str) -> bool:
        _, cfi_part, date_part, _ = fname.split("_")
        if inst_type and (cfi_part != inst_type):
            return False
        if file_date and (file_date.strftime("%Y%m%d") != date_part):
            return False
        return True

    return list(filter(test, filter(lambda s: s.startswith("FULINS"), firds_files)))
