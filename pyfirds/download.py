import logging
import os
from dataclasses import dataclass
from datetime import datetime, date
from hashlib import file_digest
from typing import Any
from zipfile import ZipFile

import requests
from dateutil import tz
from pysolr import Solr

BASE_URL = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/"

logger = logging.getLogger(__name__)


class BadChecksumError(Exception):
    """An error raised when a downloaded file does not have the expected checksum."""
    pass


@dataclass
class FirdsDoc:
    """A dataclass representing a single document reference returned by searching the FIRDS database.

    :param checksum: MD5 checksum for the file.
    :param download_link: A URL to download the file from.
    :param file_id: An ID for the file.
    :param file_name: The name of the file.
    :param file_type: The type of the file.
    :param timestamp: The timestamp of the document.
    """

    checksum: str
    download_link: str
    file_id: str
    file_name: str
    file_type: str
    timestamp: datetime

    @staticmethod
    def from_dict(d: dict[str, Any]) -> 'FirdsDoc':
        return FirdsDoc(
            d['checksum'],
            d['download_link'],
            d['id'],
            d['file_name'],
            d['file_type'],
            d['timestamp']
        )

    def download_zip(self, to_dir: str, overwrite: bool = False, verify: bool = True):
        """Download this file as a zip file to the specified directory.

        :param to_dir: The directory to download the file to.
        :param overwrite: Whether to overwrite an existing file if one already exists. Default is False.
        :param verify: Whether to verify the checksum of the downloaded file. Default is True.
        :return: The absolute path of the file's location.
        """

        fpath = os.path.join(to_dir, self.file_name)
        if os.path.exists(fpath) and not overwrite:
            raise FileExistsError(fpath)

        fpath_part = f'{fpath}.part'

        with requests.get(self.download_link, stream=True) as r:
            r.raise_for_status()
            with open(fpath_part, 'wb') as fd:
                logger.info(f'Downloading file from {self.download_link} to {fpath}.')
                for chunk in r.iter_content(1024 * 8):
                    fd.write(chunk)
        os.rename(fpath_part, fpath)

        if verify:
            logger.info(f'Verifying checksum of file at {fpath}.')
            with open(fpath, 'rb') as fd:
                check = file_digest(fd, 'md5').hexdigest()
                if check != self.checksum:
                    raise BadChecksumError(f'File {fpath} has checksum {check}, expected {self.checksum}.')

        return fpath

    def download_xml(self, to_dir: str, overwrite: bool = False, verify: bool = True, delete_zip: bool = True):
        """Download this file as an XML file to the specified directory.

        :param to_dir: The directory to download the file to. If no directory is specified, a temporary one is used.
        :param overwrite: Whether to overwrite an existing file if one already exists. Default is False.
        :param verify: Whether to verify the checksum of the downloaded zip file. Default is True.
        :param delete_zip: Whether to delete the zip file after its contents have been extracted. Default is True.
        :return: The absolute path of the file's location.
        """

        zip_fpath = self.download_zip(to_dir, overwrite=overwrite, verify=verify)
        with open(zip_fpath, 'rb') as fd:
            zip_file = ZipFile(fd)
            xml_fname = zip_file.namelist()[0]
            xml_fpath = os.path.join(to_dir, xml_fname)
            if os.path.exists(xml_fpath) and not overwrite:
                raise FileExistsError(xml_fpath)
            logger.debug(f'Extracting {zip_fpath} to {xml_fpath}.')
            zip_file.extractall(to_dir)

        if delete_zip:
            logger.debug(f'Deleting {zip_fpath}.')
            os.remove(zip_fpath)

        return os.path.join(to_dir, xml_fname)


class FirdsSearcher:

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.solr = Solr(base_url)

    def search(self, from_date: date, to_date: date, query: str = '*') -> list[FirdsDoc]:
        """Search the FIRDS database and return a list of download URLs.

        :param from_date: The start of the period to search. Can be a :class:`datetime` object or a :class:`date`
            object. In the latter case, the search period will run from the start of that date.
        :param to_date: The end of the period to search. Can be a :class:`datetime` object or a :class:`date` object.
            In the latter case, the search period will run to the end of that date.
        :param query: The query to search. Optional, but can be set to 'FULINS', 'DLTINS' or 'FULCAN' to search for full
            FIRDS records, delta files or cancellation files, respectively.
        """

        logger.debug(f'Searching FIRDS database for query {query} from {from_date} to {to_date}.')

        start = 0
        rows = 100

        if not isinstance(from_date, datetime):
            from_date = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0)
        if not isinstance(to_date, datetime):
            to_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 999)

        from_str = from_date.astimezone(tz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        to_str = to_date.astimezone(tz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        pub_date_fq = f'publication_date:[{from_str} TO {to_str}]'
        results = self.solr.search(query, fq=pub_date_fq, start=start, rows=rows)
        hits = results.hits
        logger.info(f"Found {hits} results. Query took {results.qtime}ms.")
        docs = [FirdsDoc.from_dict(d) for d in results.docs]
        while hits > (start + rows):
            start += rows
            results = self.solr.search(query, fq=pub_date_fq, start=start, rows=rows)
            logger.info(f"Got results {start} to {start + rows} of {hits}. Query took {results.qtime}ms.")
            docs.extend(FirdsDoc.from_dict(d) for d in results.docs)
        return docs
