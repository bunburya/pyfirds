Basic usage
===========

Downloading
-----------

The `download` module contains functions functions and classes to help you download FIRDS files from ESMA or the FCA.

You can get a list of files meeting your search criteria (date range and, optionally, file type) using the ``search``
method of an :class:`.EsmaFirdsSearcher` or :class:`.FcaFirdsSearcher` object as appropriate. :meth:`.EsmaFirdsSearcher.search`
(or :meth:`.FcaFirdsSearcher.search`) will return a list of :class:`.FirdsDoc` objects, each representing a FIRDS file
that is available for download.

.. code-block:: python

    from datetime import date
    from pyfirds.download import EsmaFirdsSearcher
    searcher = EsmaFirdsSearcher()
    docs = searcher.search(from_date=date(2025, 1, 1), to_date=date(2025, 1, 7), file_type="FULINS")  # A list of FirdsDoc objects

You can download a zip file using the :meth:`.FirdsDoc.download_zip` method, or download and unzip the file using
the :meth:`.FirdsDoc.download_xml` method. You can choose whether or not to overwrite existing files and whether to
verify ESMA FIRDS files using the checksum provided (FCA FIRDS does not provide checksums for file verification, so
passing ``verify=True`` when downloading an FCA FIRDS file will emit a warning that the file has not been verified).

``pyfirds`` includes a convenience script, ``firds-dl.py``, that you can use to download FIRDS files using the command
line. Call ``firds-dl --help`` for usage information.

Parsing
-------

The most convenient way to parse an XML FIRDS file is to use the :func:`.xml_utils.iterparse` function. This will
iteratively parse the XML file and yield instances of relevant dataclasses (eg, :class:`.ReferenceData`) as it
encounters corresponding XML tags. Due to the size of the FIRDS files, it is not generally advisable to parse the entire
files into memory at the same time (unless you are sure you have sufficient RAM).

.. code-block:: python

    from pyfirds.xml_utils import iterparse
    firds_file = "/path/to/FULINS_C_20250201_01of01.xml"
    for ref_data in iterparse(firds_file, {"RefData": ReferenceData}):
        # ref_data is a ReferenceData object
        do_something(ref_data)

.. note::

    Because of the size of the FIRDS files (each of which can contain hundreds of thousands of data points),
    working with them can be rather slow and cumbersome. Moderate your expectations accordingly. Code contributions with
    a view to making parsing more performant are always welcome.