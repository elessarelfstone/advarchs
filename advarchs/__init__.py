import re
import os
import sys
import itertools
import string
import subprocess as subp
from mailbox import Message
from itertools import groupby
from subprocess import DEVNULL

import requests

from advarchs.utils import file_ext

__version__ = '0.1.4'

__all__ = ['webfilename', 'extract_web_archive']

SEVEN_Z = '7z'


CONSOLE_CODING = 'utf8'
if sys.platform == 'win32':
    CONSOLE_CODING = 'cp866'

ARCHIVE_COMPRESS_FORMATS = ('rar', 'tar', 'zip', 'gzip', 'bzip')

REMOVE_PUNCTUATION = dict((ord(char), None) for char in string.punctuation if char not in '._-')


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
            raise DownloadException('Could not download file.' + e.message)


def _7z_error_message(raw):
    """ Return error message from raw 7z's stderr"""
    def clean(s):
        return s.strip().split('\n')[-1]

    # we need only get message that goes after ERROR or ERRORS
    pattern = r"ERROR:\s?(.*\r\n.*)|ERRORS:\r\n(.*)"
    search_result = re.findall(pattern, raw, re.M)
    err_iter = itertools.chain.from_iterable(search_result)
    return '. '.join(list(filter(None, set(clean(i) for i in err_iter))))


def test_7z():
    """Check if 7z installed or not"""
    try:
        subp.Popen([SEVEN_Z], stdout=DEVNULL, stderr=DEVNULL)
        result = True
    except OSError:
        result = False

    return result


def test_archive(apath):
    """Check if archive corrupted"""
    args = [SEVEN_Z, 't', apath]
    call_result = subp.Popen(args, stdout=subp.PIPE, stderr=subp.PIPE)
    stdout, stderr = call_result.communicate()
    if (call_result.returncode != 0) or (not re.search(r"Everything is Ok", stdout.decode(CONSOLE_CODING))):
        error_message = _7z_error_message(stderr.decode(CONSOLE_CODING))
        raise ExtractException(error_message)
    return True


def archive_info(apath):
    """Get info about archive and its content"""

    def parse_files_info_list(raw):
        """Return directories and files list from 7z's raw stdout with details"""
        blocks = []
        current_block = {}
        # make flat list of clean stdout's lines
        lines = [line.strip() for line in raw.strip().split('\n')]
        # break down flat list with details on lists for each file in archive
        block_list = [list(g) for k, g in groupby(lines, lambda x: x != '') if k]

        for block in block_list:
            for line in block:
                key, _, value = line.partition('=')
                current_block[key.strip().lower()] = value.strip()
            blocks.append(current_block)
            current_block = {}

        return blocks

    def parse_archive_tech_info(raw):
        """Return tech details of archive"""
        arch_info = {}
        for line in raw.strip().split('\n'):
            key, _, value = line.partition('=')
            arch_info[key.strip().lower()] = value.strip().lower()

        return arch_info

    args = [SEVEN_Z, 'l', '-slt', apath]
    call_result = subp.Popen(args, stdout=subp.PIPE)
    stdout, _ = call_result.communicate()
    if call_result.returncode != 0:
        raise ExtractException('Subprocess returned non-zero exit code. Could not get archive info.')

    raw_list = re.sub(r"^-+", '-'*10, stdout.decode(CONSOLE_CODING), flags=re.MULTILINE).split('-'*10)
    return parse_archive_tech_info(raw_list[1]), parse_files_info_list(raw_list[2])


def _extract_file(apath, file):
    dfolder = '-o' + os.path.dirname(apath)
    args = [SEVEN_Z, 'e', '-aoa', apath, file, dfolder]
    call_result = subp.Popen(args, stdout=subp.PIPE)
    stdout, _ = call_result.communicate()
    if call_result.returncode != 0:
        raise ExtractException('Subprocess returned non-zero exit code. Could not extract archive.')
    out_file = os.path.join(os.path.dirname(apath), file)

    return out_file


def extract(apath, ffilter=[]):
    """ Extract files to same directory"""
    _out_files = []

    def aformat(ainfo):
        a_format = ''
        if ainfo["path"]:
            # basic sanitize
            a_format = ''.join([i for i in ainfo["type"] if not i.isdigit()]).lower()
        return a_format

    def is_matched(afile):
        """ Check if file in archive should be extracted """
        if ffilter:
            # we check only full name and extension of file
            if (os.path.basename(afile) in ffilter) or (file_ext(afile) in ffilter):
                return True
            else:
                return False

    def is_archive(afile):
        """ Check if there is another archive inside or it's compressed archive like tar.gz """
        return file_ext(os.path.basename(afile)) in ARCHIVE_COMPRESS_FORMATS
        # return aformat(ainfo) in ARCHIVE_COMPRESS_FORMATS

    def extract_recur(curr_apath):
        """Extract current archive and if there are archives inside it will be called for them
        @return: paths of extracted files
        """
        a_info, a_content = archive_info(curr_apath)

        # this real checking, cause we checking 7z info but not just extension of file
        if aformat(a_info) in ARCHIVE_COMPRESS_FORMATS:
            f_paths = [f["path"] for f in a_content]
            for f in f_paths:
                if is_matched(f):
                    buff = _extract_file(curr_apath, f)
                    _out_files.append(buff)
                if is_archive(f):
                    tmp = _extract_file(curr_apath, f)
                    extract_recur(tmp)
        else:
            raise ExtractException(a_info["path"] + ' is not archive')

    if test_7z():
        extract_recur(apath)
    else:
        raise ExtractException('7z is not installed')
    return _out_files


def extract_web_archive(url, apath, ffilter=[]):
    """ Download archive and extract all or specified files"""
    try:
        download(url, apath)
    except DownloadException:
        if os.path.exists(apath):
            os.remove(apath)
        raise

    output_files = []

    if test_archive(apath):
        output_files = extract(apath, ffilter=ffilter)

    return output_files
