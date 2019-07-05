import os
import cgi
from pathlib import Path
import re
import zipfile

import rarfile
import requests


class Utils:
    @staticmethod
    def read_file(file, encoding="utf8"):
        with open(file, "r", encoding=encoding) as f:
            result = f.read()
        return result

    @staticmethod
    def webfilename(url):
        h = requests.get(url, stream=True)
        fname = ''
        if "content-disposition" in map(str.lower, h.headers.keys()):
            # raw = re.findall("filename=(.+)", h.headers["content-disposition"])[0]
            raw = h.headers["content-disposition"]
            headers = cgi.parse_header(raw)
            for header in headers:
                if isinstance(header, dict):
                    fname = header["filename"]

            if not fname:
                fname = headers
        else:
            fname = url.split("/")[-1]

        return fname

    @staticmethod
    def download(url, dpath, name):
        try:
            r = requests.get(url)
            # build path for downloading file
            f_path = os.path.join(dpath, name)
            with open(f_path, 'wb') as f:
                f.write(r.content)
            return f_path
        except Exception as e:
            raise e

    @staticmethod
    def file_ext(f):
        return Path(f).suffix.replace('.', '')


