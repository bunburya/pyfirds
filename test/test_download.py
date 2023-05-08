import os
import logging
import random

from lxml import etree

from pyfirds.download import FirdsSearch, BASE_URL

from test.values import get_test_run_dir, TEST_DATA_DIR, search_params_to_checksums

RUN_DIR = get_test_run_dir(__name__)

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

firds = FirdsSearch(BASE_URL)

def test_01_search():
    for from_time, to_time, q in search_params_to_checksums:
        results = firds.search(from_time, to_time, q)
        checks = search_params_to_checksums[(from_time, to_time, q)]
        assert len(results) == len(checks)
        for r, c in zip(results, checks):
            assert r.checksum == c
            if q != '*':
                assert r.file_type == q

def test_02_download():
    for from_time, to_time, q in search_params_to_checksums:
        results = firds.search(from_time, to_time, q)
        for r in random.choices(results, k=min(10, len(results))):
            xml_fpath = r.download_xml(RUN_DIR, overwrite=True, verify=True, delete_zip=True)
            logger.debug(f'Testing parsing of XML file {xml_fpath}.')
            etree.parse(xml_fpath)
            os.remove(xml_fpath)




