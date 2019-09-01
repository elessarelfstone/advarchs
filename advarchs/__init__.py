import os
import shutil
import string

from mailbox import Message

import requests

from advarchs.utils import file_ext, extract_version
from advarchs.handlers import (HandlersFactory, AdvarchsException,
                               ArchiveStatus, SevenZHandler, RarHandler)

ARCHIVE_COMPRESS_FORMATS = ('rar', 'tar', 'zip', 'gzip', 'bzip', 'gz')

__version__ = extract_version(__file__)


__all__ = ['webfilename', 'extract_web_archive']


REMOVE_PUNCTUATION = dict((ord(char), None) for char in string.punctuation if char not in '._-')

if os.name == 'nt':
    if shutil.which('7z'):
        HandlersFactory.register('7z', SevenZHandler('7z', ))
        # HandlersFactory.register('unrar', RarHandler('unrar', ))
    else:
        raise AdvarchsException('Unpacker is not installed.')
elif os.name == 'posix':
    if (shutil.which('7z') or shutil.which('7za')) and (shutil.which('unrar')):
        HandlersFactory.register('7z', SevenZHandler('7z')) if shutil.which('7z') else HandlersFactory.register('7za', SevenZHandler('7za'))
        HandlersFactory.register('unrar', RarHandler('unrar'))
    elif ((shutil.which('7z') or shutil.which('7za')) and not (shutil.which('unrar'))):
        HandlersFactory.register('7z', SevenZHandler('7z')) if shutil.which('7z') else HandlersFactory.register('7za', SevenZHandler('7za'))
    else:
        raise AdvarchsException('Unpacker is not installed.')


class ExtractException(Exception):
    pass


class DownloadException(Exception):
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
            raise AdvarchsException('Could not download file.' + e.message)


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
    status = ArchiveStatus.NOT_COMPATIBLE
    handlers = HandlersFactory.handlers()
    for handler in dict(handlers):
        unpacker = handlers[handler]
        status = unpacker.check(apath)
        if unpacker.check(apath) == ArchiveStatus.ALL_GOOD:
            return handler
    if status == ArchiveStatus.CORRUPTED:
        raise AdvarchsException('Could not unpack. Archive is corrupted')
    elif status == ArchiveStatus.NOT_COMPATIBLE:
        raise AdvarchsException('Could not unpack. Archive format is not supported')
    elif status == ArchiveStatus.UNKNOWN_ERROR:
        raise AdvarchsException('Could not unpack. Unknown error')


def extract(apath, ffilter=[]):
    """Extract all or specified files from archive"""
    # handler = resolve_format(apath)
    # unpacker_handler = HandlersFactory.get_handler(handler )
    # out_files = unpacker_handler.extract(apath, ffilter)
    # return out_files
    _extracted_files = []
    _is_nested = False

    def extract_recursive(curr_apath):
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
    try:
        download(url, apath)
    except DownloadException:
        if os.path.exists(apath):
            os.remove(apath)
        raise

    output_files = extract(apath, ffilter=ffilter)
    return output_files


# t = resolve_format("c:\\Users\\elessar\\Documents\\test_archives\\test_advarchs_to_extract.rar")
# fs = extract("c:\\Users\\elessar\\Documents\\test_archives\\КАТО_12_17.rar", ffilter=["katonew1.xls"])

