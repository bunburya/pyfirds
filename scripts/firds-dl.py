#!/usr/bin/env python

import logging
import os
from argparse import ArgumentParser
from datetime import datetime, date

from pyfirds.download import EsmaFirdsSearcher


def get_argparser() -> ArgumentParser:
    a = ArgumentParser(description="Download FIRDS XML data files.")
    a.add_argument("-u", "--unzip", dest="unzip", action="store_true", help="Unzip the downloaded files. By default, "
                                                                            "removes the zip files; pass --keep-zip to "
                                                                            "keep them.")
    a.add_argument("-k", "--keep-zip", action="store_true", help="Keep zip files after unzipping. "
                                                                 "Only relevant if --unzip has been passed.")
    a.add_argument("-d", "--debug", action="store_true", help="More verbose logging.")
    a.add_argument("-q", "--query", metavar="QUERY_STRING", default="*",
                   help="A query string, compatible with Solr or Elasticsearch (as appropriate), "
                        "which can be used to refine the search.")
    a.add_argument("-t", "--to-dir", metavar="PATH", default=os.path.curdir,
                   help="Path to the directory to save the files to.")
    a.add_argument("-o", "--overwrite", action="store_true", help="Overwrite files that are already on disk.")
    a.add_argument("from_date", metavar="DATE",
                   help="Date and time from which to search (inclusive), in YYYY-MM-DD format.")
    a.add_argument("to_date", metavar="DATE",
                   help="Date and time to which to search (inclusive), in YYYY-MM-DD format.")
    return a


def search(argparser: ArgumentParser):
    ns = argparser.parse_args()
    if ns.debug:
        logging.basicConfig(level=logging.DEBUG)
    print(f"Searching for `{ns.query}` from {ns.from_date} to {ns.to_date}.")
    s = EsmaFirdsSearcher()
    docs = s.search(from_date=date.fromisoformat(ns.from_date), to_date=date.fromisoformat(ns.to_date), query=ns.query)
    num_docs = len(docs)
    print(f"Found {num_docs} documents.")
    if num_docs == 0:
        return
    if not os.path.exists(ns.to_dir):
        print(f"{ns.to_dir} does not exist. Creating it.")
        os.makedirs(ns.to_dir)
    for i, doc in enumerate(docs):
        print(f"Downloading {i + 1}/{num_docs}: {doc.file_name}")
        if ns.unzip:
            print(f"Unzipping {doc.file_name}.")
            try:
                doc.download_xml(ns.to_dir, overwrite=ns.overwrite, delete_zip=not ns.keep_zip)
            except FileExistsError:
                print(f"{doc.file_name} already exists in {ns.to_dir}. Skipping.")
        else:
            doc.download_zip(ns.to_dir)

if __name__ == "__main__":
    search(get_argparser())