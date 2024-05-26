import os
import json
import appdirs
from typing import Optional, List, Dict, Any
import tempfile
from .remote import RemoteCfg

class RepoSettings:
    def __init__(self):
        self.url: str = ""
        self.file: str = ""
        self.cache: str = ""
        self.active_quests: List[str] = []
        self.done_tasks: List[str] = []
        self.show_url: bool  = True
        self.show_done: bool = True
        self.show_init: bool = True
        self.show_todo: bool = True
        self.game_mode: bool = True

    def get_file(self) -> str:
        if self.file == "" or os.path.exists(self.file) == False:
            if self.url != "":
                # download file from url to tempfile
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    self.file = f.name
                    cfg = RemoteCfg()
                    cfg.from_url(self.url)
                    cfg.download_absolute(self.file)
        return self.file

    def set_file(self, file: str):
        self.file = file
        return self

    def set_url(self, url: str):
        self.url = url
        return self

    def to_dict(self):
        return {
            "url": self.url,
            "file": self.file,
            "cache": self.cache,
            "active_quests": self.active_quests,
            "done_tasks": self.done_tasks,
            "show_url": self.show_url,
            "show_done": self.show_done,
            "show_init": self.show_init,
            "show_todo": self.show_todo,
            "game_mode": self.game_mode
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.url = data.get("url", "")
        self.file = data.get("file", "")
        self.cache = data.get("cache", "")
        self.active_quests = data.get("active_quests", [])
        self.done_tasks = data.get("done_tasks", [])
        self.show_url = data.get("show_url", True)
        self.show_done = data.get("show_done", True)
        self.show_init = data.get("show_init", True)
        self.show_todo = data.get("show_todo", True)
        self.game_mode = data.get("game_mode", True)
        return self

    def __str__(self) -> str:
        return (
            f"URL: {self.url}\n"
            f"File: {self.file}\n"
            f"Cache: {self.cache}\n"
            f"Active Quests: {self.active_quests}\n"
            f"Done Tasks: {self.done_tasks}\n"
            f"Show URL: {self.show_url}\n"
            f"Show Done: {self.show_done}\n"
            f"Show Init: {self.show_init}\n"
            f"Show Todo: {self.show_todo}\n"
            f"Game Mode: {self.game_mode}\n"
        )

class LocalSettings:
    def __init__(self):
        self.lang: str = "ask"
        self.ascii: bool = False
        self.color: bool = True
        self.updown: bool = True
        self.sideto_min: int = 60

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lang": self.lang,
            "ascii": self.ascii,
            "color": self.color,
            "updown": self.updown,
            "sideto_min": self.sideto_min
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.lang = data.get("lang", "ask")
        self.ascii = data.get("ascii", False)
        self.color = data.get("color", True)
        self.updown = data.get("updown", True)
        self.sideto_min = data.get("sideto_min", 60)
        return self

    def __str__(self) -> str:
        return (
            f"Default Language: {self.lang}\n"
            f"Encoding Mode: {'ASCII' if self.ascii else 'UNICODE'}\n"
            f"Color Mode: {'COLORED' if self.color else 'MONOCHROMATIC'}\n"
            f"Diff Mode: {'SIDE_BY_SIDE' if self.updown else 'UP_DOWN'}\n"
            f"Side-to-Side Min: {self.sideto_min}\n"
        )

class Settings:
    def __init__(self):
        self.reps: Dict[str, RepoSettings] = {}
        self.local = LocalSettings()
        self.reps["fup"] = RepoSettings().set_url("https://github.com/qxcodefup/arcade/blob/master/Readme.md")
        self.reps["ed"] = RepoSettings().set_url("https://github.com/qxcodeed/arcade/blob/master/Readme.md")
        self.reps["poo"] = RepoSettings().set_url("https://github.com/qxcodepoo/arcade/blob/master/Readme.md")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reps": {k: v.to_dict() for k, v in self.reps.items()},
            "local": self.local.to_dict()
        }

    def from_dict(self, data: Dict[str, Any]):
        self.reps = {k: RepoSettings().from_dict(v) for k, v in data.get("reps", {}).items()}
        self.local = LocalSettings().from_dict(data.get("local", {}))
        return self
    
    def save_to_json(self, file: str):
        with open(file, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


class SettingsParser:

    __settings_file: Optional[str] = None

    def __init__(self, settings_file: Optional[str] = None):
        if settings_file is not None:
            SettingsParser.__settings_file = settings_file
        self.package_name = "tko"
        self.filename = "settings.json"
        if SettingsParser.__settings_file is None:
            SettingsParser.__settings_file = os.path.join(appdirs.user_data_dir(self.package_name), self.filename)
        else:
            SettingsParser.__settings_file = os.path.abspath(SettingsParser.__settings_file)
        self.settings = self.load_settings()

    @staticmethod
    def set_settings_file(settings_file: str):
        SettingsParser.__settings_file = settings_file

    @staticmethod
    def get_settings_file() -> Optional[str]:
        return SettingsParser.__settings_file


    def load_settings(self) -> Settings:
        try:
            with open(SettingsParser.__settings_file, "r") as f:
                return Settings().from_dict(json.load(f))
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            return self.create_new_settings_file()

    def save_settings(self):
        self.settings.save_to_json(SettingsParser.__settings_file)


    def create_new_settings_file(self) -> Settings:
        self.settings = Settings()
        if not os.path.isdir(self.get_settings_dir()):
            os.makedirs(self.get_settings_dir(), exist_ok=True)
        self.save_settings()
        return self.settings

    def get_settings_dir(self) -> str:
        return os.path.dirname(SettingsParser.__settings_file)
    
    def get_language(self) -> str:
        return self.settings.local.lang

    def get_repository(self, course: str) -> Optional[str]:
        rep = self.settings.reps.get(course, None)
        if rep is not None:
            if rep.url != "":
                print(rep.url)
                cfg = RemoteCfg()
                cfg.from_url(rep.url)
                cfg.file = ""
                git_raw = "https://raw.githubusercontent.com"
                url = f"{git_raw}/{cfg.user}/{cfg.repo}/{cfg.branch}/base/"
                print("debug:", url)
                return url

if __name__ == "__main__":
    print("ping")
    sp = SettingsParser("x.json")
    rfup = sp.settings.reps["fup"]
    rfup.get_file()
    sp.save_settings()
    print(str(sp))
