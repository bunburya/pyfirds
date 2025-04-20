# pyfirds

`pyfirds` is a library for working with [Financial Instruments Reference Database System](https://en.wikipedia.org/wiki/Financial_Instruments_Reference_Database_System)
data published by the [European Securities and Markets Authority](https://data.europa.eu/data/datasets/financial-instruments-reference-data-system?locale=en) (ESMA)
in the EU and the [Financial Conduct Authority](https://www.fca.org.uk/markets/transaction-reporting/instrument-reference-data) (FCA) in the UK.
It includes code for searching and downloading the XML files from both ESMA and the FCA, and parsing that XML into dataclasses.

The `firds-dl.py` script in the `scripts/` directory allows you to easily download the XML files. Call `firds-dl --help` for usage details.

The `iterparse` function in the `xml_utils` module parses a FIRDS XML file and yields instances of the relevant dataclasses describing the data.
Elements are deleted once they are processed to preserve memory (the files are quite large so loading the entire tree into memory at once can take a lot of RAM).