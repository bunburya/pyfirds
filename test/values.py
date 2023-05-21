import os
from datetime import datetime
from shutil import rmtree

TEST_DATA_DIR = os.path.join("test_data")
TEST_RUN_BASE_DIR = os.path.join(TEST_DATA_DIR, "run")
TEST_FIRDS_DATA_DIR = os.path.join(TEST_DATA_DIR, "firds_data")

if not os.path.exists(TEST_RUN_BASE_DIR):
    os.makedirs(TEST_RUN_BASE_DIR)

def get_test_run_dir(name: str) -> str:
    dir_path = os.path.join(TEST_RUN_BASE_DIR, name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

