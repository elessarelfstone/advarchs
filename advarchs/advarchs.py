import os
import shutil
import zipfile

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
        self.name = name
        self.tempdir = tempdir
        self.files_ext = files_ext
        self.files_cnt = files_cnt

    def _fileslist_to_download_by_list(self, arch_obj):
        """
        Get files in archive to extract applying list-filter of names
        :param arch_obj: object of archive (RarFile, ZipFile, etc)
        :return: list of files name
        """
        files = []
        for file in arch_obj.namelist():
            if file in self.files_ext:
                files.append(file)
        return files

    def _fileslist_to_download_by_ext(self, arch_obj):
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
        arch_handler = self._arch_handler(fpath)
        return arch_handler(fpath)

    def _arch_handler(self, fpath):
        return ArchsHandlersFactory.get_handler(Utils.file_ext(fpath))

    def _extract_file(self, arch_obj, arch_file, fpath):
        arch_obj.extract(arch_file, self.tempdir)
        tmp_path = os.path.join(self.tempdir, arch_file).replace('/', os.sep)
        shutil.move(tmp_path, fpath)

    def _download_arch(self, url, suff=""):
        """
        Download archive from internet and name it as we want
        :param url: url in internet
        :param suff: part of name we build
        :return: path of new downloaded file
        """
        name = f'{self.name}_{suff}' if suff else self.name
        f_path = Utils.download(url, self.tempdir, name)
        return f_path

    def output_paths(self, suff=""):
        """
        Get result output paths of files after extracting
        :param suff: one of the parts of file's name
        :return: list of files's paths
        """

        files = []
        name_parts = [self.name]
        if suff:
            name_parts.append(suff)
        #TODO change the way of getting list of output files. download whole file and digg into that

        if isinstance(self.files_ext, str):
            for i in range(self.files_cnt):
                name_parts.append(str(i))
                f_path = os.path.join(self.tempdir, '_'.join(name_parts)+'.'+self.files_ext)
                files.append(f_path)
                name_parts.pop()
        return files

    def extract_from_webarchive(self, url, id=""):
        f_path = self._download_arch(url, id)
        arch_obj = self._arch_object(f_path)
        if isinstance(self.files_ext, list):
            files_in_arch = self._fileslist_to_download_by_list(arch_obj)
        else:
            files_in_arch = self._fileslist_to_download_by_ext(arch_obj)

        output_files = self.output_paths(id)

        if len(files_in_arch) != len(output_files):
            raise Exception('Count of {} file format and count given are not equal'.format(self.filter))

        for arch_file, output_file in zip(files_in_arch, output_files):
            self._extract_file(arch_obj, arch_file, output_file)

        return output_files



