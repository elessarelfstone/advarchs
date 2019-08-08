========
Advarchs
========


Overview
========
Advarchs is simple tool for retrieving data from web archives.
Sometimes it can be useful if you are working with data represented
as like Excel files or other format. But there is problem, it's packed and
the only way get it is to download it. Also you have to do processing
stuff periodically, cause data is being updated from time to time. You can
write a lots of code doing boring things as downloading and extracting.
Or you can use Advarchs to get all the data files you need by adding
a few lines to your code.


.. code-block::

    from advarchs import extract_web_archive

    url = "http://www.site.com/archive.rar"
    out_files = extract_web_archive(url, "c:\new.rar", ffilter=[])

Requirements
============
* 3.5+
* 7z utility installed

Install
=======

.. code-block::

    pip install advarchs

