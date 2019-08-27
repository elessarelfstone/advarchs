import abc
import re
import os
import sys
from enum import Enum
from itertools import chain, groupby

from advarchs.utils import run_with_output, file_ext


CONSOLE_CODING = 'utf8'
if sys.platform == 'win32':
    CONSOLE_CODING = 'cp866'


class ArchiveStatus(Enum):
    ALL_GOOD = 0
    NOT_COMPATIBLE = 1
    CORRUPTED = 2
    UNKNOWN_ERROR = 3


class AdvarchsException(Exception):
    pass


class ArchiveHandlerBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def unpacker(self):
        return

    @abc.abstractmethod
    def files_list(self, apath):
        """Get archive's content"""
        return

    @abc.abstractmethod
    def check(self, apath):
        """Test archive for corruption or etc"""
        return

    @abc.abstractmethod
    def extract(self, apath, ffilter):
        """Extract files from archive"""
        return


class HandlersFactory:

    _handlers = {}

    @classmethod
    def get_handler(cls, name):
        try:
            return cls._handlers[name]
        except KeyError:
            raise ValueError(name)

    @classmethod
    def register(cls, name, handler):
        cls._handlers[name] = handler

    @classmethod
    def handlers(cls):
        return cls._handlers


class SevenZHandler(ArchiveHandlerBase):

    formats = ('tar', 'zip', 'gzip', 'bzip')
    re_not_compatible_pattern = r"Can not open the file as archive"
    re_success_pattern = r"Everything is Ok"
    re_corruption_pattern = r"Data Error"

    def __init__(self, unpacker):
        self._unpacker = unpacker

    def _files_info(self, apath):
        r, out, _ = run_with_output([self.unpacker(), 'l', '-slt', apath], CONSOLE_CODING)
        raw = re.sub(r"^-+", '-' * 10, out, flags=re.MULTILINE).split('-' * 10)[2]
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

    def _tech_info(self, apath):
        r, out, _ = run_with_output([self.unpacker(), 'l', '-slt', apath], CONSOLE_CODING)
        raw = re.sub(r"^-+", '-' * 10, out, flags=re.MULTILINE).split('-' * 10)[1]
        t_info = {}
        for line in raw.strip().split('\n'):
            key, _, value = line.partition('=')
            t_info[key.strip().lower()] = value.strip().lower()

        return t_info

    def unpacker(self):
        return self._unpacker

    def check(self, apath):
        r, out, err = run_with_output([self.unpacker(), 't', apath], CONSOLE_CODING)
        if r == 0:
            return ArchiveStatus.ALL_GOOD
        else:
            if not re.search(self.re_success_pattern, out):
                if re.search(self.re_not_compatible_pattern, err):
                    return ArchiveStatus.NOT_COMPATIBLE
                elif re.search(self.re_corruption_pattern, err):
                    return ArchiveStatus.CORRUPTED
                else:
                    return ArchiveStatus.UNKNOWN_ERROR

    def files_list(self, apath):
        a_files_info = self._files_info(apath)
        return [f["path"] for f in a_files_info]

    def extract(self, apath, afile):
        dfolder = '-o' + os.path.dirname(apath)
        args = [self.unpacker(), 'e', '-aoa', apath, afile, dfolder]
        r, out, err = run_with_output(args, CONSOLE_CODING)
        if r != 0:
            raise AdvarchsException('Could not extract archive.')
        f_path = os.path.join(os.path.dirname(apath), afile)

        return f_path


class RarHandler(ArchiveHandlerBase):

    re_not_compatible_pattern = r"is not RAR archive"
    re_success_pattern = r"All OK"
    re_corruption_pattern = r"Total errors:"

    def __init__(self, unpacker):
        self._unpacker = unpacker

    def unpacker(self):
        return self._unpacker

    def _files_info(self, apath):
        r, out, _ = run_with_output([self.unpacker(), 'ltab', apath], CONSOLE_CODING)
        raw = re.search(r"([ \t]*Name:.*?)(?=(\n{1,2}Service:\s*EOF|\Z))", out, re.M | re.S).group(1)
        blocks = []
        current_block = {}
        # make flat list of clean stdout's lines
        lines = [line.strip() for line in raw.strip().split('\n')]
        # break down flat list with details on lists for each file in archive
        block_list = [list(g) for k, g in groupby(lines, lambda x: x != '') if k]

        for block in block_list:
            for line in block:
                key, _, value = line.partition(': ')
                current_block[key.strip().lower()] = value.strip()
            blocks.append(current_block)
            current_block = {}

        return blocks

    def files_list(self, apath):
        a_files_info = self._files_info(apath)
        return [f["name"] for f in a_files_info if "type" in f.keys() and f["type"].lower() == "file"]

    def check(self, apath):
        r, out, err = run_with_output([self.unpacker(), 't', apath], CONSOLE_CODING)
        if r == 0:
            return ArchiveStatus.ALL_GOOD
        else:
            if not re.search(self.re_success_pattern, out):
                if re.search(self.re_not_compatible_pattern, out):
                    return ArchiveStatus.NOT_COMPATIBLE
                elif re.search(self.re_corruption_pattern, out):
                    return ArchiveStatus.CORRUPTED
                else:
                    return ArchiveStatus.UNKNOWN_ERROR

    def extract(self, apath, afile):

        args = [self.unpacker(), 'e', '-o+', apath, afile]
        r, out, err = run_with_output(args, CONSOLE_CODING, cwd=os.path.dirname(apath))
        if r != 0:
            raise AdvarchsException('Could not extract archive.')
        f_path = os.path.join(os.path.dirname(apath), afile)

        return f_path
