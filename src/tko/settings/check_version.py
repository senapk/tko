from urllib.request import urlopen
from typing import Optional
from .. import __version__

class CheckVersion:

    link = "https://raw.githubusercontent.com/senapk/tko/master/src/tko/__init__.py"

    def __init__(self):
        self.version: str = __version__
        self.latest_version: Optional[str] = self.get_latest_version()

    def version_check(self):
        if self.latest_version is None:
            return
        if self.version != self.latest_version:
            major, minor, patch = [int(x) for x in self.version.split(".")]
            latest_major, latest_minor, latest_patch = [int(x) for x in self.latest_version.split(".")]
            if major < latest_major or (major == latest_major and minor < latest_minor) or (major == latest_major and minor == latest_minor and patch < latest_patch):
                print(f"Sua versão do  TKO ({self.version}) está desatualizada.")
                print(f"A última versão é a {self.latest_version}.")

    def get_latest_version(self):
        try:
            with urlopen(self.link) as f:
                for line in f:
                    if b"__version__" in line:
                        return line.decode().split('"')[1]
        except:
            return None