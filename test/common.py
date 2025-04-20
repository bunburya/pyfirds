import logging
import os
from dataclasses import fields
from typing import Any, Type

logger = logging.getLogger(__name__)

TEST_DATA_DIR = os.path.join("test_data")
TEST_RUN_BASE_DIR = os.path.join(TEST_DATA_DIR, "run")
TEST_FIRDS_DATA_DIR = os.path.join(TEST_DATA_DIR, "firds_data")

FIRDS_DIR = os.path.join(TEST_DATA_DIR, "firds_data")
ESMA_FIRDS_DIR = os.path.join(FIRDS_DIR, "esma")
FCA_FIRDS_DIR = os.path.join(FIRDS_DIR, "fca")

try:
    ESMA_FIRDS_FILES = os.listdir(ESMA_FIRDS_DIR)
except FileNotFoundError as e:
    logger.critical(f"Could not file ESMA FIRDS file directory ({ESMA_FIRDS_DIR}). This directory should be present and "
                    "should contain FIRDS files downloaded from ESMA website to test against.")
    logger.exception(e)
    raise e

try:
    FCA_FIRDS_FILES = os.listdir(FCA_FIRDS_DIR)
except FileNotFoundError as e:
    logger.critical(f"Could not file FCA FIRDS file directory ({FCA_FIRDS_DIR}). This directory should be present and "
                    "should contain FIRDS files downloaded from FCA website to test against.")
    logger.exception(e)
    raise e

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
