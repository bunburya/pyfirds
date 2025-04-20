import logging
import os
from argparse import ArgumentParser
from datetime import date

from pyfirds.download import FcaFirdsSearcher, EsmaFirdsSearcher


def get_argparser() -> ArgumentParser:
    a = ArgumentParser(description="Download FIRDS XML data files.")
    a.add_argument("-u", "--unzip", dest="unzip", action="store_true", help="Unzip the downloaded files. By default, "
                                                                            "removes the zip files; pass --keep-zip to "
                                                                            "keep them.")
    a.add_argument("-k", "--keep-zip", action="store_true", help="Keep zip files after unzipping. "
                                                                 "Only relevant if --unzip has been passed.")
    a.add_argument("-d", "--debug", action="store_true", help="More verbose logging.")
    a.add_argument("-t", "--file-type", choices=['fulins', 'dltins', 'fulcan'], help="The type of FIRDS file to download.")
    a.add_argument("-o", "--overwrite", action="store_true", help="Overwrite files that are already on disk.")
    a.add_argument("-s", "--source", choices=["esma", "fca"], default="esma",
                   help="Source to download data from (ESMA or FCA).")
    a.add_argument("from_date", metavar="DATE",
                   help="Date and time from which to search (inclusive), in YYYY-MM-DD format.")
    a.add_argument("to_date", metavar="DATE",
                   help="Date and time to which to search (inclusive), in YYYY-MM-DD format.")
    a.add_argument("dest", metavar="DIR", default=os.path.curdir,
                   help="Directory to save the files to. Will be created if it does not exist.")
    return a


def search(argparser: ArgumentParser):
    ns = argparser.parse_args()
    file_type = ns.file_type.upper() if ns.file_type else None
    if ns.debug:
        logging.basicConfig(level=logging.DEBUG)
    print(f"Searching for files of type `{file_type or 'any'}` from {ns.from_date} to {ns.to_date}.")
    s = EsmaFirdsSearcher() if ns.source.lower() == "esma" else FcaFirdsSearcher()
    docs = s.search(from_date=date.fromisoformat(ns.from_date), to_date=date.fromisoformat(ns.to_date), file_type=file_type)
    num_docs = len(docs)
    print(f"Found {num_docs} documents.")
    if num_docs == 0:
        return
    if not os.path.exists(ns.dest):
        print(f"{ns.dest} does not exist. Creating it.")
        os.makedirs(ns.dest)
    for i, doc in enumerate(docs):
        print(f"Downloading {i + 1}/{num_docs}: {doc.file_name}")
        zip_path = os.path.join(ns.dest, doc.file_name)
        unzip_path = zip_path[:-4] + ".xml"
        if (not ns.overwrite) and os.path.exists(unzip_path):
            # If unzipped file already exists and we're not overwriting it, don't even try to download the zip
            print(f"{unzip_path} already exists. Skipping.")
            continue
        try:
            if ns.unzip:
                print(f"Unzipping {doc.file_name}.")
                doc.download_xml(ns.dest, overwrite=ns.overwrite, delete_zip=not ns.keep_zip)
            else:
                doc.download_zip(ns.dest, overwrite=ns.overwrite)
        except FileExistsError as e:
            print(f"{e.args[0]} already exists. Skipping.")

def firds_dl():
    search(get_argparser())
