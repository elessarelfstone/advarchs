import os
import string
from contextlib import contextmanager

import pytest

from advarchs import __version__
from advarchs import download, filename_from_content_disposition, webfilename
from advarchs import archive_info, extract, extract_web_archive
from advarchs.utils import get_hash_memory_optimized, file_ext

from tests.fixtures import local_archives

from tests import TEMP_DIR

remove_punctuation_map = dict((ord(char), None) for char in string.punctuation if char not in '._-')


@contextmanager
def webfile(url):
    webfname = webfilename(url)
    # webfname = webfname.translate(remove_punctuation_map)
    fpath = os.path.join(TEMP_DIR, webfname)
    yield fpath
    if os.path.exists(fpath):
        os.remove(fpath)


@contextmanager
def localfile(fpath):
    yield fpath
    if os.path.exists(fpath):
        os.remove(fpath)


def test_version():
    assert __version__ == '0.1.1'


class TestDownloadUtils:

    @pytest.mark.parametrize(
        'header, expected_filename', [
        ('attachment; filename=hello-WORLD_123.txt', 'hello-WORLD_123.txt'),
        ('attachment; filename=".hello-WORLD_123.txt"', 'hello-WORLD_123.txt'),
        ('attachment; filename="white space.txt"', 'white space.txt'),
        (r'attachment; filename="\"quotes\".txt"', '"quotes".txt'),
        ('attachment; filename=/etc/hosts', 'hosts'),
        ('attachment; filename=', None)
    ]
    )
    def test_filename_from_content_disposition(self, header, expected_filename):
        assert filename_from_content_disposition(header) == expected_filename

    @pytest.mark.parametrize(
        'url', [
            ('https://drive.google.com/uc?export=download&id=1No0RIFMYJ7ymw7PT5id3JRh9Zu4UoZVj'),
            ('https://gist.github.com/elessarelfstone/627a59a72bb82826b8b23022fb92b446/raw/a6ebf46b805593dc8163d50f4eec3035f3e669e6/test_advarchs_direct_link.rar'),
            ('https://drive.google.com/uc?export=download&id=1cenn13H4u6YbNeusXyTp_eSeFAGvf06m'),
            ('https://drive.google.com/uc?export=download&id=1sJVR5oeknyt-dgpwZQ_ElVfywZ6UmlIm'),
        ]
    )
    def test_download(self, url):
        with webfile(url) as apath:
            f_size = download(url, apath)
            assert os.path.exists(apath)
            assert f_size > 0


class TestAdvArchs:
    def test_archive_info(self, local_archives):
        apath, _ = local_archives
        arch_info = archive_info(apath)
        assert len(arch_info[0]) > 0
        assert len(arch_info[1]) > 0

    def test_extract_with_ext_as_filter(self, local_archives):
        apath, files_hashes = local_archives
        f_exts = [file_ext(f) for f in files_hashes.keys()]
        out_files = extract(apath, f_exts)
        for o_f in out_files:
            assert os.path.exists(apath)
            assert os.path.basename(o_f) in files_hashes.keys()
            assert get_hash_memory_optimized(o_f) == files_hashes[os.path.basename(o_f)]

    def test_extract_with_filename_as_filter(self, local_archives):
        apath, files_hashes = local_archives
        out_files = extract(apath, files_hashes.keys())
        for o_f in out_files:
            assert os.path.basename(o_f) in files_hashes.keys()
            assert get_hash_memory_optimized(o_f) == files_hashes[os.path.basename(o_f)]

    @pytest.mark.parametrize(
        'url, ffilter, files', [
            ('https://gist.github.com/elessarelfstone/627a59a72bb82826b8b23022fb92b446/raw/48262cf304f33e396ea7f36f3c4c3b98698c0a48/test_advarchs_to_extract.rar',
             ['html', 'js', 'dumper.png'],
             ['index.html', 'bootstrap.js', 'dumper.png']
             )
        ]
    )
    def test_extract_web_archive(self, url, ffilter, files):
        with webfile(url) as apath:
            out_files = extract_web_archive(url, apath, ffilter=ffilter)
            for o_f in out_files:
                with localfile(o_f) as fpath:
                    assert os.path.basename(fpath) in files
