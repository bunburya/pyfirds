import logging
import os
from datetime import date

from sqlalchemy import create_engine

from common import get_fulins, FIRDS_DIR, TEST_RUN_BASE_DIR
from pyfirds.db.dao import FirdsDao
from pyfirds.db.schema import metadata
from pyfirds.model import ReferenceData
from pyfirds.xml import iterparse

DB_FILE = os.path.join(TEST_RUN_BASE_DIR, "test.db")
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

def test_01_build_database():
    """Test building a database from FULINS files."""
    fulins_20210320 = get_fulins(file_date=date(2021, 3, 20))
    engine = create_engine(f"sqlite:///{DB_FILE}")
    metadata.create_all(engine)
    dao = FirdsDao(engine)
    last_row_id = 0
    with engine.connect() as conn:
        for f in fulins_20210320:
            fpath = os.path.join(FIRDS_DIR, f)
            for ref_data in iterparse(fpath, {"RefData": ReferenceData}):
                valid_from = ref_data.technical_attributes.publication_period.from_date
                row_id = dao.add_reference_data(ref_data, conn, valid_from)
                assert row_id == last_row_id + 1
                last_row_id += 1
                if not (last_row_id % 10000):
                    conn.commit()
        conn.commit()

