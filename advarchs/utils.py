import os
import hashlib
import tarfile
import subprocess as subp
from random import choice, randint
from string import ascii_uppercase
from zipfile import ZipFile
from pathlib import Path

import tomlkit


def extract_version(source_file):
    """ Extract package version from pyproject file """
    d = Path(source_file)
    result = None
    while d.parent != d and result is None:
        d = d.parent
        pyproject_toml_path = d / 'pyproject.toml'
        if pyproject_toml_path.exists():
            with open(file=str(pyproject_toml_path)) as f:
                pyproject_toml = tomlkit.parse(string=f.read())
                if 'tool' in pyproject_toml and 'poetry' in pyproject_toml['tool']:
                    # noinspection PyUnresolvedReferences
                    result = pyproject_toml['tool']['poetry']['version']
    return result


def get_hash_memory_optimized(f_path, mode='sha256'):
    """ Get hash of file"""
    h = hashlib.new(mode)
    with open(f_path, 'rb') as file:
        block = file.read(4096)
        while block:
            h.update(block)
            block = file.read(4096)

    return h.hexdigest()


def read_file(file, encoding="utf8"):
    """ Simple reading text file """
    with open(file, "r", encoding=encoding) as f:
        result = f.read()
    return result


def create_file(file, data, encoding="utf8"):
    """ Create text file and return hash of it """
    with open(file, "w", encoding=encoding) as f:
        f.write(data)
    return get_hash_memory_optimized(file)


def add_file_to_zip(fpath, apath):
    """ Add file to zip archive"""
    with ZipFile(apath, 'a') as zip_o:
        zip_o.write(fpath, arcname=os.path.basename(fpath))


def add_file_to_tar(fpath, apath):
    """ Add file to tar archive"""
    with tarfile.open(apath, "a") as tar_o:
        tar_o.add(fpath, arcname=os.path.basename(fpath))


def file_ext(f):
    """ File extension """
    return Path(f).suffix.replace('.', '')


def random_string(min_l, max_l):
    """ Get random text of length ranging from min_l to max_l """
    return ''.join(choice(ascii_uppercase) for i in range(randint(min_l, max_l)))


def run_with_output(args, encoding, **kwargs):
    """ Run program """
    res = subp.Popen(args, stdout=subp.PIPE, stderr=subp.PIPE, **kwargs)
    stdout, stderr = res.communicate()
    return res.returncode, stdout.decode(encoding).lower(), stderr.decode(encoding).lower()

