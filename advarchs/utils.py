import os
import hashlib
import tarfile
from random import choice, randint
from string import ascii_uppercase
from zipfile import ZipFile

from pathlib import Path


def get_hash_memory_optimized(f_path, mode='sha256'):
    h = hashlib.new(mode)
    with open(f_path, 'rb') as file:
        block = file.read(4096)
        while block:
            h.update(block)
            block = file.read(4096)

    return h.hexdigest()


def read_file(file, encoding="utf8"):
    with open(file, "r", encoding=encoding) as f:
        result = f.read()
    return result


def create_file(file, data, encoding="utf8"):
    with open(file, "w", encoding=encoding) as f:
        f.write(data)
    return get_hash_memory_optimized(file)


def add_file_to_zip(fpath, apath):
    # if not os.path.exists(archpath):
    with ZipFile(apath, 'a') as zip_o:
        zip_o.write(fpath, arcname=os.path.basename(fpath))


def add_file_to_tar(fpath, apath):
    with tarfile.open(apath, "a") as tar_o:
        tar_o.add(fpath, arcname=os.path.basename(fpath))
        # tar_o.addfile(tarfile.TarInfo(os.path.basename(fpath)), open(fpath, "r"))


def file_ext(f):
    return Path(f).suffix.replace('.', '')


def random_string(min_val, max_val):
    return ''.join(choice(ascii_uppercase) for i in range(randint(min_val, max_val)))
