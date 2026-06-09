from platformdirs import user_cache_dir, user_data_dir
from pathlib import Path

class UserData:
    PACKAGE_NAME = 'tko'

    @staticmethod
    def global_cache_dir() -> Path:
        folder = Path(user_cache_dir(appname=UserData.PACKAGE_NAME)) / "cache"
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def settings_dir() -> Path:
        dir = Path(user_data_dir(UserData.PACKAGE_NAME))
        if not dir.exists():
            dir.mkdir(parents=True, exist_ok=True)
        return dir