import os

import pytest

from advarchs.utils import (
    create_file,
    add_file_to_zip,
    add_file_to_tar,
    random_string)

from tests import TEMP_DIR


TEST_LOCAL_ARCHIVES = [
    ("zip_test_local", add_file_to_zip, ["local_test.jpg", "local_test.png", "local_test.docx"
                        ,"local_test.xlsx", "local_test.exe", "local_test1.txt"]),

    ("tar_test_local", add_file_to_tar, ["local_test.bin", "local_test2.psd", "local_test2.ini"]),

]


@pytest.fixture(params=TEST_LOCAL_ARCHIVES)
def local_archives(request):
    arch = request.param
    f_paths = []
    f_hashes = {}
    arch_name, arch_handler, files = arch
    frmt = arch_name.split('_')[0]
    arch_path = os.path.join(TEMP_DIR, "{}.{}".format(arch_name, frmt))
    for f in files:
        f_path = os.path.join(TEMP_DIR, f)
        f_paths.append(f_path)
        sha = create_file(f_path, random_string(500, 1000))
        f_hashes[f] = sha
        arch_handler(f_path, arch_path)

    for f in f_paths:
        os.remove(f)

    yield arch_path, f_hashes

    os.remove(arch_path)









