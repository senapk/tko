
import os
import re
import configparser

from typing import List, Optional
import urllib.request
from tko.util.remote_md import RemoteLink, RemoteCfg, Absolute

class RemoteUrl:
    def __init__(self, url: str):
        self.raw_link: str | None = ""
        self.remote: RemoteLink | None = None

        if not url.startswith("https://"):
            raise ValueError("Invalid URL")

        if url.startswith("https://gist.githubusercontent.com"):
            self.raw_link = url
        else:
            self.remote = RemoteLink().identify_from_url(url)
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
        try:
            content = open(tempfile, encoding="utf-8").read()
        except:
            content = open(tempfile).read()
        if self.remote is not None:
            content = Absolute.relative_to_absolute(content, self.remote)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content.encode("utf-8").decode("utf-8"))
        return

    def __str__(self):
        return self.get_raw_url()
