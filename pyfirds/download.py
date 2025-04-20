import abc
import logging
import os
from dataclasses import dataclass
from datetime import datetime, date
from enum import StrEnum
from hashlib import file_digest
from typing import Any, Optional
from zipfile import ZipFile

import requests
from dateutil import tz
from pysolr import Solr

from pyfirds._firds_dl import firds_dl

ESMA_BASE_URL = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/"
FCA_BASE_URL = "https://api.data.fca.org.uk/fca_data_firds_files"

logger = logging.getLogger(__name__)


class FileType(StrEnum):
    """The type of a FIRDS data file."""

    FULINS = "FULINS"
    DLTINS = "DLTINS"
    FULCAN = "FULCAN"

class BadChecksumError(Exception):
    """An error raised when a downloaded file does not have the expected checksum."""
    pass


@dataclass
class FirdsDoc:
    """A dataclass representing a single document reference returned by searching a FIRDS database (ESMA or FCA)."""

    download_link: str
    """A URL to download the file from."""
    file_id: str
    """An ID for the file."""
    file_name: str
    """The name of the file."""
    file_type: str
    """The type of the file (FULINS/DLTINS/FULCAN)."""
    timestamp: datetime
    """The timestamp of the document."""
    checksum: Optional[str]
    """MD5 checksum for the file, if present (should be present in ESMA data but not FCA data)."""

    @classmethod
    def from_esma_dict(cls, d: dict[str, Any]) -> 'FirdsDoc':
        return cls(
            download_link=d["download_link"],
            file_id=d["id"],
            file_name=d["file_name"],
            file_type=d["file_type"],
            timestamp=d["timestamp"],
            checksum=d.get("checksum")
        )

    @classmethod
    def from_fca_dict(cls, d: dict[str, Any]) -> 'FirdsDoc':
        return cls(
            download_link=d["_source"]["download_link"],
            file_id=d["_id"],
            file_name=d["_source"]["file_name"],
            file_type=d["_source"]["file_type"],
            timestamp=datetime.fromisoformat(d["_source"]["last_refreshed"]),
            checksum=None
        )

    def download_zip(self, to_dir: str, overwrite: bool = False, verify: bool = True):
        """Download this file as a zip file to the specified directory.

        :param to_dir: The directory to download the file to.
        :param overwrite: Whether to overwrite an existing file if one already exists. Default is False.
        :param verify: Whether to verify the checksum of the downloaded file. Default is True.
        :return: The absolute path of the file's location.
        """

        fpath = os.path.join(to_dir, self.file_name)
        if (not overwrite) and os.path.exists(fpath):
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
            if self.checksum is None:
                logger.warning("Cannot verify file as no checksum was provided.")
            else:
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
            if (not overwrite) and os.path.exists(xml_fpath):
                raise FileExistsError(xml_fpath)
            logger.debug(f'Extracting {zip_fpath} to {xml_fpath}.')
            zip_file.extractall(to_dir)

        if delete_zip:
            logger.debug(f'Deleting {zip_fpath}.')
            os.remove(zip_fpath)

        return os.path.join(to_dir, xml_fname)

class BaseFirdsSearcher(abc.ABC):

    @abc.abstractmethod
    def search(self, from_date: date, to_date: date, file_type: Optional[FileType]) -> list[FirdsDoc]:
        """Search the FIRDS database and return a list of download URLs.

        :param from_date: The start of the period to search. Can be a :class:`datetime` object or a :class:`date`
            object. In the latter case, the search period will run from the start of that date.
        :param to_date: The end of the period to search. Can be a :class:`datetime` object or a :class:`date` object.
            In the latter case, the search period will run to the end of that date.
        :param file_type: The query to search. Optional, but can be `FULINS`, `DLTINS` or `FULCAN` to search for full
            FIRDS records, delta files or cancellation files, respectively.
        """
        raise NotImplementedError

class EsmaFirdsSearcher(BaseFirdsSearcher):

    def __init__(self, base_url: str = ESMA_BASE_URL):
        self.base_url = base_url
        self.solr = Solr(base_url)

    def search(self, from_date: date, to_date: date, file_type: Optional[FileType]) -> list[FirdsDoc]:

        query = file_type or "*"
        logger.debug(f'Searching ESMA FIRDS database for query {query} from {from_date} to {to_date}.')

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
        logger.info(f"Found {hits} results. Got results {start} to {start + len(results.docs)}. Query took {results.qtime}ms.")
        docs = [FirdsDoc.from_esma_dict(d) for d in results.docs]
        while hits > (start + rows):
            start += rows
            results = self.solr.search(query, fq=pub_date_fq, start=start, rows=rows)
            logger.info(f"Got results {start} to {start + len(results.docs)} of {hits}. Query took {results.qtime}ms.")
            docs.extend(FirdsDoc.from_esma_dict(d) for d in results.docs)
        return docs

class FcaFirdsSearcher(BaseFirdsSearcher):
    def __init__(self, base_url: str = FCA_BASE_URL):
        self.base_url = base_url

    @staticmethod
    def _build_q(from_date: date, to_date: date, file_type: Optional[FileType] = None) -> str:
        """Builds a general query to be used as the `q` parameter to the request.

        :param from_date: The start date of the period to search.
        :param to_date: The end date of the period to search.
        :param file_type: The specific file type to search for (if not provided, all file types will be returned).
        """
        from_str = from_date.strftime("%Y-%m-%d")
        to_str = to_date.strftime("%Y-%m-%d")
        q = f"(publication_date:[{from_str}%20TO%20{to_str}])"
        if file_type is not None:
            q += f"%20AND%20(file_type:{file_type})"
        return f"({q})"

    def search(self, from_date: date, to_date: date, file_type: Optional[FileType] = None) -> list[FirdsDoc]:
        start = 0
        rows = 100
        q = self._build_q(from_date, to_date, file_type)
        results = requests.get(self.base_url, params={"q": q, "from": start, "size": rows})
        results.raise_for_status()
        j = results.json()
        data = j["hits"]
        hit_count = data["total"]
        hits = data["hits"]
        logger.info(f"Found {hit_count} results. Got results {start} to {start + len(hits)} Query took {j['took']}ms.")
        docs = [FirdsDoc.from_fca_dict(d) for d in hits]
        while hit_count > (start + rows):
            start += rows
            results = requests.get(self.base_url, params={"q": q, "from": start, "size": rows})
            results.raise_for_status()
            j = results.json()
            data = j["hits"]
            hits = data["hits"]
            logger.info(f"Got results {start} to {start + len(hits)} of {hit_count}. Query took {j['took']}ms.")
            docs.extend(FirdsDoc.from_fca_dict(d) for d in hits)
        return docs

