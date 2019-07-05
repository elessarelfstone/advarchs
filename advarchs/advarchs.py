import os
import shutil
import zipfile
import tarfile
from datetime import datetime as dt

import rarfile


from advarchs.utils import Utils


class ArchsHandlersFactory:
    '''
    Just simple factory for getting right archive handler
    '''
    _handlers = {}
    @classmethod
    def get_handler(cls, name):
        try:
            return cls._handlers[name]
        except KeyError:
            raise ValueError(name)

    @classmethod
    def register(cls, name, handler):
        if name not in cls._handlers:
            cls._handlers[name] = handler


class AdvWebArchs():
    def __init__(self, name, tempdir, files_ext="", files_cnt=0):
        ArchsHandlersFactory.register('rar', rarfile.RarFile)
        ArchsHandlersFactory.register('zip', zipfile.ZipFile)
        # ArchsHandlersFactory.register('tar.gz', tarfile.TarFile)
        self.name = name
        self.tempdir = tempdir
        self.files_ext = files_ext
        self.files_cnt = files_cnt

    def _get_arch_filename(self, url, suff=""):
        ext = Utils.file_ext(Utils.webfilename(url))
        name_parts = [self.name, dt.today().strftime("%Y%m%d")]
        if suff:
            name_parts.append(suff)
        return '_'.join(name_parts) + '.' + ext

    def _fileslist_to_extract_by_ext(self, arch_obj):
        """
        Get files in archive to extract applying file's extension-filter
        :param arch_obj: object of archive (RarFile, ZipFile, etc)
        :return: list of files name
        """
        files = []
        for file in arch_obj.namelist():
            if file.split('.')[-1] == self.files_ext:
                files.append(file)
        return files

    def _arch_object(self, fpath):
        arch_handler = ArchsHandlersFactory.get_handler(Utils.file_ext(fpath))
        return arch_handler(fpath)

    def _extract_file(self, arch_obj, arch_file, fpath):
        arch_obj.extract(arch_file, self.tempdir)
        tmp_path = os.path.join(self.tempdir, arch_file).replace('/', os.sep)
        shutil.move(tmp_path, fpath)

    def _download_arch(self, url, suff=""):
        name = self._get_arch_filename(url, suff)
        f_path = Utils.download(url, self.tempdir, name)
        return f_path

    def output_paths(self, url, suff=""):
        """
        Get path of downloaded archive and list of files inside archive
        :param url: target url of archive
        :param suff: in case we need add some identity to name of files
        :return: tuple of path and list
        """
        files = []
        f_path = self._download_arch(url, suff)
        arch_obj = self._arch_object(f_path)
        files_in_arch = self._fileslist_to_extract_by_ext(arch_obj)

        for i, f in enumerate(files_in_arch):
            if not suff:
                f_name = '{}_{}.{}'.format(self.name, i, Utils.file_ext(f))
            else:
                f_name = '{}_{}_{}.{}'.format(self.name, suff, i, Utils.file_ext(f))
            f_out = os.path.join(self.tempdir, f_name)
            files.append((f, f_out))
        return f_path, files

    def extract_from_webarchive(self, url, id=""):
        """
        Download archive from web and extract files inside
        :param url: target url of archive
        :param id: in case we need add some identity to name of files
        :return: files's paths
        """
        arch_path, files = self.output_paths(url, suff=id)
        arch_obj = self._arch_object(arch_path)
        for file in files:
            self._extract_file(arch_obj, file[0], file[1])
        return [f[1] for f in files]




