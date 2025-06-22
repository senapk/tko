from urllib.request import urlopen
from tko import __version__


class CheckVersion:
    link = "https://raw.githubusercontent.com/senapk/tko/master/src/tko/__init__.py"
    buffer: str | None = None
    init: bool = False

    def __init__(self):

        self.version: str = __version__
        if not CheckVersion.init:
            CheckVersion.buffer = self.get_latest_version()
            CheckVersion.init = True
        self.latest_version: str | None = CheckVersion.buffer

    def is_updated(self):
        if self.latest_version is None:
            return True
        if self.version != self.latest_version:
            major, minor, patch = [int(x) for x in self.version.split(".")]
            latest_major, latest_minor, latest_patch = [int(x) for x in self.latest_version.split(".")]
            if major < latest_major or (major == latest_major and minor < latest_minor) or (major == latest_major and minor == latest_minor and patch < latest_patch):
                return False
        return True

    def get_latest_version(self):
        try:
            with urlopen(self.link) as f:
                for line in f:
                    if b"__version__" in line:
                        return line.decode().split('"')[1]
        except:
            return None