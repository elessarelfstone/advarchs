import os
from shutil import which
import string

from mailbox import Message

import requests

from advarchs.utils import file_ext, extract_version
from advarchs.handlers import (HandlersFactory, AdvarchsExtractException,
                               ArchiveStatus, SevenZHandler, RarHandler)


__all__ = ['webfilename', 'extract_web_archive']


ARCHIVE_COMPRESS_FORMATS = ('rar', 'tar', 'zip', 'gzip', 'bzip', 'gz')

__version__ = extract_version(__file__)


REMOVE_PUNCTUATION = dict((ord(char), None) for char in string.punctuation if char not in '._-')

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
    elif SEVENZ and not UNRAR:
        HandlersFactory.register(SEVENZ, SevenZHandler(SEVENZ))
    else:
        raise AdvarchsExtractException('Unpacker is not installed.')


class AdvarchsDownloadException(Exception):
    pass


def filename_from_content_disposition(content_disposition):
    """
    Extract and validate filename from a Content-Disposition header.
    """
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
            return f_size
        except Exception as e:
            os.remove(fpath)
            raise AdvarchsDownloadException('Could not download file.' + e.message)


def _is_matched(afile, ffilter=[]):
    """ Check if file in archive should be extracted """
    if ffilter:
        # we check only full name and extension of file
        if (os.path.basename(afile) in ffilter) or (file_ext(afile) in ffilter):
            return True
        else:
            return False
    return True


def _is_archive(afile):
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
    """Extract all or specified files from archive"""
    _extracted_files = []
    _is_nested = False

    def extract_recursive(curr_apath):
        """ Extract while archives or compression occur """
        handler = resolve_format(curr_apath)
        unpacker = HandlersFactory.get_handler(handler)
        files = unpacker.files_list(curr_apath)

        for f in files:
            if _is_matched(f, ffilter=ffilter):
                _fpath = unpacker.extract(curr_apath, f)
                _extracted_files.append(_fpath)
            if _is_archive(f):
                _apath = unpacker.extract(curr_apath, f)
                extract_recursive(_apath)

    extract_recursive(apath)
    return _extracted_files


def extract_web_archive(url, apath, ffilter=[]):
    """ Download archive and extract all or specified files"""
    download(url, apath)
    output_files = extract(apath, ffilter=ffilter)
    return output_files

