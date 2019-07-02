import os
import re
import rarfile
import zipfile
from pathlib import Path

import requests


class Utils:

    @staticmethod
    def download(url, dpath, name):
        try:
            r = requests.get(url)
            # get extension of file
            if "content-disposition" in map(str.lower, r.headers.keys()):
                tmp = re.findall("filename=(.+)", r.headers["content-disposition"])[0]
            else:
                tmp = url.split("/")[-1]
            ext = Utils.file_ext(tmp)
            # build path for downloading file
            f_path = os.path.join(dpath, f'{name}.{ext}')
            with open(f_path, 'wb') as f:
                f.write(r.content)
            return f_path
        except Exception as e:
            raise e

    @staticmethod
    def file_ext(f):
        return Path(f).suffix.replace('.', '')


