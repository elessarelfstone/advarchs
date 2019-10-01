import os
from shutil import which
import string
import tempfile

from mailbox import Message

import requests
from advarchs.utils import file_ext, extract_version, get_hash_memory_optimized
from advarchs.handlers import (HandlersFactory, AdvarchsExtractException,
                               ArchiveStatus, SevenZHandler, RarHandler)


__all__ = ['webfilename', 'extract_web_archive', 'AdvArchs']


ARCHIVE_COMPRESS_FORMATS = ('rar', 'tar', 'zip', 'gzip', 'bzip', 'gz')

__version__ = extract_version(__file__)


REMOVE_PUNCTUATION = dict((ord(char), None) for char in string.punctuation if char not in '._-')

# get appropriate cli command name for installed 7z
SEVENZ = max([a if which(a) else None for a in ('7z', '7za')], key=lambda x: bool(x), default=None)

UNRAR = 'unrar' if which('unrar') else None

if os.name == 'nt':
    if SEVENZ:
        HandlersFactory.register(SEVENZ, SevenZHandler(SEVENZ))
    else:
        raise AdvarchsExtractException('Unpacker is not installed.')
elif os.name == 'posix':
    if SEVENZ and UNRAR:
        HandlersFactory.register(SEVENZ, SevenZHandler(SEVENZ))
        HandlersFactory.register(UNRAR, RarHandler(UNRAR))
    elif SEVENZ and (not UNRAR):
        HandlersFactory.register(SEVENZ, SevenZHandler(SEVENZ))
    else:
        raise AdvarchsExtractException('Unpacker is not installed.')


class AdvarchsDownloadException(Exception):
    pass


def filename_from_content_disposition(content_disposition):
    """ Extract and validate filename from a Content-Disposition header. """
    msg = Message('Content-Disposition: %s' % content_disposition)
    filename = msg.get_filename()
    if filename:
        # Basic sanitation.
        filename = os.path.basename(filename).lstrip('.').strip()
        if filename:
            return filename


def _get_headers_from_url(url):
    with requests.get(url, stream=True) as r:
        return r.headers


def _content_disposition(headers):
    return headers.get("content-disposition")


def webfilename(url):
    """Get filename from archive's headers or from the url"""
    headers = _get_headers_from_url(url)

    if _content_disposition(headers):
        result = filename_from_content_disposition(_content_disposition(headers))
    else:
        result = url.split("/")[-1]

    return result.translate(REMOVE_PUNCTUATION)


def download(url, fpath):
    """Download file using streaming"""
    with open(fpath, 'wb') as f:
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                f_size = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        f_size += len(chunk)
                f_hash = get_hash_memory_optimized(fpath)
            return f_size, f_hash
        except Exception as e:
            os.remove(fpath)
            raise AdvarchsDownloadException('Could not download file.' + e.message)


def is_matched(afile, ffilter=[]):
    """ Check if file in archive should be extracted """
    if ffilter:
        # we check only full name and extension of file
        if (os.path.basename(afile) in ffilter) or (file_ext(afile) in ffilter):
            return True
        else:
            return False
    return True


def is_archive(afile):
    """Check if inside file can be archive or compressed"""
    return file_ext(os.path.basename(afile)) in ARCHIVE_COMPRESS_FORMATS


def resolve_format(apath):
    """ Resolve right handler for archive """

    status = ArchiveStatus.NOT_COMPATIBLE
    handlers = HandlersFactory.handlers()

    for handler in dict(handlers):
        unpacker = handlers[handler]
        status = unpacker.check(apath)
        if unpacker.check(apath) == ArchiveStatus.ALL_GOOD:
            return handler

    if status == ArchiveStatus.CORRUPTED:
        raise AdvarchsExtractException('Could not unpack. Archive is corrupted')

    elif status == ArchiveStatus.NOT_COMPATIBLE:
        raise AdvarchsExtractException('Could not unpack. Archive format is not supported')

    elif status == ArchiveStatus.UNKNOWN_ERROR:
        raise AdvarchsExtractException('Could not unpack. Unknown error')


def extract(apath, ffilter=[]):

    """ Extract files from archive """

    files = []

    def extract_recursive(curr_apath):
        """Look into archive recursively to extract files considering ffilter"""

        handler = resolve_format(curr_apath)
        unpacker = HandlersFactory.get_handler(handler)
        _files = unpacker.files_list(curr_apath)

        for f in _files:
            if is_matched(f, ffilter=ffilter):
                _fpath = unpacker.extract(curr_apath, f)
                files.append(_fpath)
            if is_archive(f):
                _apath = unpacker.extract(curr_apath, f)
                extract_recursive(_apath)

    extract_recursive(apath)
    return files


def inspect(apath):

    """ Look into archive recursively to retrieve list of all files """

    files = []

    def inspect_into(curr_apath):
        handler = resolve_format(curr_apath)
        unpacker = HandlersFactory.get_handler(handler)
        _files = unpacker.files_list(curr_apath)
        for f in _files:
            # go into nested archive or compressed file
            if is_archive(f):
                _apath = unpacker.extract(curr_apath, f)
                inspect_into(_apath)

            else:
                files.append(f)

    inspect_into(apath)
    return files


def extract_web_archive(url, apath, ffilter=[]):
    """ Download archive and extract all or specified files"""

    download(url, apath)
    output_files = extract(apath, ffilter=ffilter)

    return output_files


class AdvArchs:

    _archives = {}

    @classmethod
    def _download(cls, url, apath):
        _, f_hash = download(url, apath)
        cls._archives[apath] = f_hash

    @classmethod
    def files_list(cls, url, apath, ffilter=[]):
        """ Retrieve list of files considering ffilter"""
        files = []

        if apath not in cls._archives.keys():
            cls._download(url, apath)

        _files = inspect(apath)

        for f in _files:
            if is_matched(f, ffilter):
                files.append(f)

        return files

    @classmethod
    def extract_web_archive(cls, url, apath, ffilter=[]):
        """ Download archive and extract all or specified files"""

        if apath not in cls._archives.keys():
            download(url, apath)

        _files = extract(apath, ffilter=ffilter)

        return _files
