import os
from time import time

from pyfirds.model import ReferenceData, NewRecord, ModifiedRecord, TerminatedRecord
from pyfirds.xml import iterparse
from test.common import firds_files, FIRDS_DIR, verify_types

tags = {
    "RefData": ReferenceData,
    "NewRcrd": NewRecord,
    "ModfdRcrd": ModifiedRecord,
    "TermntdRcrd": TerminatedRecord
}

if __name__ == "__main__":
    for f in firds_files:
        print(f)
        count = {}
        t1 = time()
        for obj in iterparse(os.path.join(FIRDS_DIR, f), tags):
            t = type(obj)
            if t in count:
                count[t] += 1
            else:
                count[t] = 0
        t2 = time()
        print(f"Parsed file {f} in {t2 - t1} seconds.")
        for t in count:
            print(f"    {t}: {count[t]}")