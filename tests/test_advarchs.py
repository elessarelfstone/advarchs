import os
import tempfile

from advarchs import __version__
from advarchs.advarchs import AdvWebArchs

import pytest


TEMP_DIR = tempfile.gettempdir()


def test_version():
    assert __version__ == '0.1.0'


@pytest.fixture()
def files_in_rar():
    return {
        "url": "https://drive.google.com/uc?export=download&id=1No0RIFMYJ7ymw7PT5id3JRh9Zu4UoZVj",
        "filter": "xlsx",
        "name": "my_xlsx",
        "files_cnt": 2
    }


@pytest.fixture()
def files_in_zip():
    return {
        "url": "https://drive.google.com/uc?export=download&id=1cenn13H4u6YbNeusXyTp_eSeFAGvf06m",
        "filter": "png",
        "name": "my_png",
        "files_cnt": 1
    }


def test_output_files(files_in_rar):
    arch_engine = AdvWebArchs(files_in_rar["name"], TEMP_DIR, files_in_rar["filter"], files_in_rar["files_cnt"])
    output_files = arch_engine.output_paths()
    assert len(output_files) == 2


def test_retrieve_from_one_rar(files_in_rar):
    arch_engine = AdvWebArchs(files_in_rar["name"], TEMP_DIR, files_in_rar["filter"], files_in_rar["files_cnt"])
    output_files = arch_engine.extract_from_webarchive(files_in_rar["url"])
    assert len(output_files) != 0


def test_retrieve_from_one_zip(files_in_zip):
    arch_engine = AdvWebArchs(files_in_zip["name"], TEMP_DIR, files_in_zip["filter"], files_in_zip["files_cnt"])
    output_files = arch_engine.extract_from_webarchive(files_in_zip["url"])
    print(output_files)
    assert len(output_files) != 0



