from urllib.request import urlopen
from datetime import datetime as dt
from tko.settings.settings import Settings
from tko import __version__

class CheckVersion:
    link = "https://raw.githubusercontent.com/senapk/tko/master/src/tko/__init__.py"

    def __init__(self, settings: Settings):
        self.settings: Settings = settings
        self.user_version: str = __version__
        
    def is_updated(self):
        latest_version = self.get_latest_version()
        if latest_version == "":
            return True
        if self.user_version != latest_version:
            major, minor, patch = [int(x) for x in self.user_version.split(".")]
            latest_major, latest_minor, latest_patch = [int(x) for x in latest_version.split(".")]
            if major < latest_major or (major == latest_major and minor < latest_minor) or (major == latest_major and minor == latest_minor and patch < latest_patch):
                return False
        return True

    def get_latest_version(self) -> str:
        now = dt.now()
        last_check_str = self.settings.app.get_lastest_version_check_timestamp()
        stored_latest = self.settings.app.get_lastest_version()
        if last_check_str != "" and stored_latest != "":
            last_check = dt.fromisoformat(last_check_str)
            if (now - last_check).total_seconds() < 60 * 60 * 24: # 24h
                return stored_latest
        try:
            with urlopen(self.link, timeout=1) as f:
                for line in f:
                    if b"__version__" in line:
                        latest = line.decode().split('"')[1]
                        self.settings.app.set_latest_version_check_timestamp(now.isoformat())
                        self.settings.app.set_lastest_version(latest)
                        self.settings.save_settings()
                        return latest
        except:
            pass
        return ""