import json
import os
import tempfile

from advarchs import __version__
from advarchs.advarchs import AdvWebArchs
from advarchs.utils import Utils as ut

import pytest


TEMP_DIR = tempfile.gettempdir()


def test_version():
    assert __version__ == '0.1.0'


@pytest.fixture()
def web_rar_archives():
    web_rars = json.loads(ut.read_file('test_rars.json'))
    return web_rars


@pytest.fixture()
def web_zip_archives():
    web_zips = json.loads(ut.read_file('test_zips.json'))
    return web_zips


@pytest.fixture()
def web_tar_archives():
    web_zips = json.loads(ut.read_file('test_tars.json'))
    return web_zips


def test_output_files_in_rar(web_rar_archives):
    for arch in web_rar_archives:
        arch_engine = AdvWebArchs(arch["name"], TEMP_DIR, arch["filter"])
        out_files = arch_engine.output_paths(arch["url"])
        assert len(out_files[1]) == arch["cnt"]
        for file in arch["files"]:
            assert file in [f[0] for f in out_files[1]]


def test_output_files_in_zip(web_zip_archives):
    for arch in web_zip_archives:
        arch_engine = AdvWebArchs(arch["name"], TEMP_DIR, arch["filter"])
        out_files = arch_engine.output_paths(arch["url"])
        assert len(out_files[1]) == arch["cnt"]
        for file in arch["files"]:
            assert file in [f[0] for f in out_files[1]]


def test_output_files_in_tar(web_tar_archives):
    for arch in web_tar_archives:
        arch_engine = AdvWebArchs(arch["name"], TEMP_DIR, arch["filter"])
        out_files = arch_engine.output_paths(arch["url"])
        assert len(out_files[1]) == arch["cnt"]
        for file in arch["files"]:
            assert file in [f[0] for f in out_files[1]]


def test_retrieve_from_one_rar(web_rar_archives):
    for arch in web_rar_archives:
        arch_engine = AdvWebArchs(arch["name"], TEMP_DIR, arch["filter"])
        out_files = arch_engine.extract_from_webarchive(arch["url"])
        assert len(out_files) == arch["cnt"]
        for f in out_files:
            assert os.path.exists(f)


def test_retrieve_from_one_zip(web_zip_archives):
    for arch in web_zip_archives:
        arch_engine = AdvWebArchs(arch["name"], TEMP_DIR, arch["filter"])
        out_files = arch_engine.extract_from_webarchive(arch["url"])
        assert len(out_files) == arch["cnt"]
        for f in out_files:
            assert os.path.exists(f)
