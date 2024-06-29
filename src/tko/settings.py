import os
import json
import appdirs
import tempfile
from .util.remote import RemoteCfg, Absolute
from typing import Any, List, Dict, Optional

class RepoSettings:
    def __init__(self, file: str = ""):
        self.lang: str = ""
        self.url: str = ""
        self.file: str = ""
        self.expanded: List[str] = []
        self.new_items: List[str] = []
        self.tasks: Dict[str, str] = {} #notas das tarefas
        self.view: List[str] = []  # lista de flags ligados
        if file != "":
            self.file = os.path.abspath(file)

    def get_file(self) -> str:
        # arquivo existe e é local
        if self.file != "" and os.path.exists(self.file) and self.url == "":
            return self.file
        
        # arquivo não existe e é remoto
        if self.url != "" and (self.file == "" or not os.path.exists(self.file)):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                filename = f.name
                cfg = RemoteCfg(self.url)
                cfg.download_absolute(filename)
            return filename

        # arquivo é local com url remota
        if self.file != "" and os.path.exists(self.file) and self.url != "":
            content = open(self.file, encoding="utf-8").read()
            content = Absolute.relative_to_absolute(content, RemoteCfg(self.url))
            with tempfile.NamedTemporaryFile(delete=False) as f:
                filename = f.name
                f.write(content.encode("utf-8"))
            return filename

        raise ValueError("fail: file not found or invalid settings to download repository file")
        
    def set_file(self, file: str):
        self.file = os.path.abspath(file)
        return self
    
    def set_lang(self, lang: str):
        self.lang = lang
        return self

    def set_url(self, url: str):
        self.url = url
        return self

    def to_dict(self):
        return {
            "lang": self.lang,
            "expanded": self.expanded,
            "new_items": self.new_items,
            "url": self.url,
            "file": self.file,
            "quests": self.expanded,
            "tasks": self.tasks,
            "view": self.view
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.lang = data.get("lang", "")
        self.url = data.get("url", "")
        self.file = data.get("file", "")
        # self.expanded = data.get("expanded", [])
        #verify if expanded is a dict, being get list of values
        try:
            self.expanded = list(data.get("quests", {}).values())
        except AttributeError:
            self.expanded = data.get("expanded", [])
        self.new_items = data.get("new_items", [])
        self.tasks = data.get("tasks", {})
        self.view = data.get("view", [])
        return self

    def __str__(self) -> str:
        return (
            f"url: {self.url}\n"
            f"file: {self.file}\n"
            f"Active: {self.expanded}\n"
            f"Tasks: {self.tasks}\n"
            f"View: {self.view}\n"
        )


class LocalSettings:
    def __init__(self):
        self.rootdir: str = ""
        self.lang: str = ""
        self.ascii: bool = False
        self.color: bool = True
        self.updown: bool = True
        self.sideto_min: int = 60

    def set_rootdir(self, rootdir: str):
        self.rootdir = os.path.abspath(rootdir)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rootdir": self.rootdir,
            "lang": self.lang,
            "ascii": self.ascii,
            "color": self.color,
            "updown": self.updown,
            "sideto_min": self.sideto_min
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.rootdir = data.get("rootdir", "")
        self.lang = data.get("lang", "")
        self.ascii = data.get("ascii", False)
        self.color = data.get("color", True)
        self.updown = data.get("updown", True)
        self.sideto_min = data.get("sideto_min", 60)
        return self

    def __str__(self) -> str:
        lang = "always ask" if self.lang == "" else self.lang
        return (
            f"Root Directory: {self.rootdir}\n"
            f"Default Language: {lang}\n"
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
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    def __str__(self):
        output = ["Repositories:"]
        maxlen = max([len(key) for key in self.reps])
        for key in self.reps:
            prefix = f"- {key.ljust(maxlen)}"
            if self.reps[key].file and self.reps[key].url:
                output.append(f"{prefix} : dual   : {self.reps[key].url} ; {self.reps[key].file}")
            elif self.reps[key].url:
                output.append(f"{prefix} : remote : {self.reps[key].url}")
            else:
                output.append(f"{prefix} : local  : {self.reps[key].file}")
        return "\n".join(output)


class SettingsParser:

    user_settings_file: Optional[str] = None

    def __init__(self):
        self.package_name = "tko"
        default_filename = "settings.json"
        if SettingsParser.user_settings_file is None:
            self.settings_file = os.path.abspath(default_filename)  # backup for replit, dont remove
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), default_filename)
        else:
            self.settings_file = os.path.abspath(SettingsParser.user_settings_file)
        self.settings = self.load_settings()

    def get_settings_file(self):
        return self.settings_file

    def load_settings(self) -> Settings:
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.settings = Settings().from_dict(data)
                return self.settings
        except (FileNotFoundError, json.decoder.JSONDecodeError) as _e:
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
