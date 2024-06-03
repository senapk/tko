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
        self.quests: Dict[str, str] = {}
        self.tasks: Dict[str, str] = {}
        self.view: List[str] = ["done", "init", "link", "todo"]

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
        self.file = os.path.abspath(file)
        return self

    def set_url(self, url: str):
        self.url = url
        return self

    def to_dict(self):
        return {
            "url": self.url,
            "file": self.file,
            "cache": self.cache,
            "quests": self.quests,
            "tasks": self.tasks,
            "view": self.view
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.url = data.get("url", "")
        self.file = data.get("file", "")
        self.cache = data.get("cache", "")
        self.quests = data.get("quests", {})
        self.tasks = data.get("tasks", {})
        self.view = data.get("view", [])
        return self

    def __str__(self) -> str:
        return (
            f"url: {self.url}\n"
            f"file: {self.file}\n"
            f"cache: {self.cache}\n"
            f"Quests: {self.quests}\n"
            f"Tasks: {self.tasks}\n"
            f"View: {self.view}\n"
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

    def get_repo(self, course: str) -> RepoSettings:
        if course not in self.reps:
            raise ValueError(f"Course {course} not found in settings")
        return self.reps[course]
    
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

    user_settings_file: Optional[str] = None

    def __init__(self):
        self.package_name = "tko"
        default_filename = "settings.json"
        if SettingsParser.user_settings_file is None:
            self.settings_file = os.path.abspath(default_filename) # backup for replit, dont remove
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), default_filename)
        else:
            self.settings_file = os.path.abspath(SettingsParser.user_settings_file)
        self.settings = self.load_settings()

    def load_settings(self) -> Settings:
        try:
            with open(self.settings_file, "r") as f:
                self.settings = Settings().from_dict(json.load(f))
                return self.settings
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            return self.create_new_settings_file()

    def save_settings(self):
        self.settings.save_to_json(self.settings_file)

    def create_new_settings_file(self) -> Settings:
        self.settings = Settings()
        if not os.path.isdir(self.get_settings_dir()):
            os.makedirs(self.get_settings_dir(), exist_ok=True)
        self.save_settings()
        return self.settings

    def get_settings_dir(self) -> str:
        return os.path.dirname(self.settings_file)
    
    def get_language(self) -> str:
        return self.settings.local.lang


