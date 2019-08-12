Advarchs: Data retrieval from remote archives
=============================================

.. image:: https://img.shields.io/pypi/v/advarchs.svg
   :target: https://pypi.python.org/pypi/advarchs
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/advarchs.svg
   :target: https://pypi.python.org/pypi/advarchs
   :alt: Supported Python Versions

.. image:: https://img.shields.io/travis/elessarelfstone/advarchs/master.svg
   :target: https://travis-ci.org/elessarelfstone/advarchs
   :alt: Build Status

.. image:: https://img.shields.io/badge/wheel-yes-brightgreen.svg
   :target: https://pypi.python.org/pypi/advarchs
   :alt: Wheel Status

Overview
--------
Advarchs is simple tool for retrieving data from web archives.
It is especially useful if you are working with remote data stored in compressed
spreadsheets or of similar format.

Getting Started
---------------

Say you need to perform some data anlytics on an excel spreadsheet that gets
refreshed every month and stored in RAR format. You can target a that file
and convert it to a pandas_ dataframe with the following procedure:

.. code-block:: python

    import pd
    import os
    import tempfile
    from advarchs import webfilename,extract_web_archive

    TEMP_DIR = tempfile.gettempdir()

    url = "http://www.site.com/archive.rar"
    arch_file_name = webfilename(url)
    arch_path = os.path.join(TEMP_DIR, arch_file_name)
    xlsx_files = extract_web_archive(url, arch_path, ffilter=['xlsx'])
    for xlsx_f in xlsx_files:
        xlsx = pd.ExcelFile(xlspath)

    ...

Requirements
------------

* Python 3.5+
* 7z utility installed

Installation
------------

.. code-block:: shell

    pip install advarchs

Contributing
------------
See `CONTRIBUTING`_

Code of Conduct
~~~~~~~~~~~~~~~
This project adheres to the `Contributor Covenant 1.2`_.
By participating, you are advised to adhere to this Code of Conduct in all your
interactions with this project.

License
-------

`Apache-2.0`_

.. _`pandas`: https://pypi.org/project/pandas/
.. _`CONTRIBUTING`: https://github.com/elessarelfstone/advarchs/blob/master/CONTRIBUTING.md
.. _`Contributor Covenant 1.2`: http://contributor-covenant.org/version/1/2/0
.. _`Apache-2.0`: https://github.com/elessarelfstone/advarchs/blob/master/LICENSE
