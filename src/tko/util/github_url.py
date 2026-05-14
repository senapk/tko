# from typing import override
import urllib.request
from tko.feno.github_url_structure import GithubUrlStructure
from tko.feno.link_rebase import LinkRebase
from tko.util.decoder import Decoder

class GitHubUrl:
    def __init__(self, url: str):
        self.raw_link: str | None = ""
        self.url_structure: GithubUrlStructure | None = None

        if not url.startswith("https://"):
            raise ValueError("Invalid URL")

        if url.startswith("https://gist.githubusercontent.com"):
            self.raw_link = url
        else:
            try:
                self.url_structure = GithubUrlStructure().from_url(url)
            except ValueError as _:
                raise Warning("URL inválida para download: {}".format(url))
        self.file = ""

    def get_raw_url(self):
        if self.raw_link:
            return self.raw_link
        if self.url_structure is None:
            return ""
        return self.url_structure.raw_github_url

    def download_and_rebase(self, filename: str):
        [tempfile, __content] = urllib.request.urlretrieve(self.get_raw_url(), filename)
        content = Decoder.load(tempfile)
        if self.url_structure is not None:
            content = LinkRebase.rebase(content, self.url_structure)
        Decoder.save(filename, content)
        return

    def __str__(self):
        return self.get_raw_url()
