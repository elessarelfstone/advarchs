from advarchs.utils import Utils as ut

import pytest


@pytest.fixture()
def files_in_web():
    return[
        ('rar', 'test_arch_few_files.rar', 'https://drive.google.com/uc?export=download&id=1No0RIFMYJ7ymw7PT5id3JRh9Zu4UoZVj'),
        ('zip', 'test_arch_few_files.zip', 'https://drive.google.com/uc?export=download&id=1cenn13H4u6YbNeusXyTp_eSeFAGvf06m')
    ]


@pytest.fixture()
def files_ext_in_web():
    return[
        ('rar', 'https://drive.google.com/uc?export=download&id=1No0RIFMYJ7ymw7PT5id3JRh9Zu4UoZVj'),
        ('zip', 'https://drive.google.com/uc?export=download&id=1cenn13H4u6YbNeusXyTp_eSeFAGvf06m')
    ]


def test_webfilename(files_in_web):
    for f in files_in_web:
        assert ut.webfilename(f[2]) == f[1]


def test_webfilename_ext(files_in_web):
    for f in files_in_web:
        assert ut.file_ext(ut.webfilename(f[2])) == f[0]