
import os
import re
import configparser

from typing import List, Optional
import urllib.request
from tko.feno.remote_md import RemoteLink, Absolute
from tko.util.decoder import Decoder

class RemoteUrl:
    def __init__(self, url: str):
        self.raw_link: str | None = ""
        self.remote: RemoteLink | None = None

        if not url.startswith("https://"):
            raise ValueError("Invalid URL")

        if url.startswith("https://gist.githubusercontent.com"):
            self.raw_link = url
        else:
            try:
                self.remote = RemoteLink().identify_from_url(url)
            except:
                raise Warning("URL inválida para download: {}".format(url))
        self.file = ""

    def get_raw_url(self):
        if self.raw_link:
            return self.raw_link
        if self.remote is None:
            return ""
        return "https://raw.githubusercontent.com/" + self.remote.user + "/" + self.remote.repo + "/" + self.remote.branch + "/" + self.remote.folder + "/" + self.remote.file

    def download_absolute_to(self, filename: str):
        [tempfile, __content] = urllib.request.urlretrieve(self.get_raw_url(), filename)
        content = ""
        content = Decoder.load(tempfile)
        if self.remote is not None:
            content = Absolute.relative_to_absolute(content, self.remote)
        Decoder.save(filename, content)
        return

    def __str__(self):
        return self.get_raw_url()
