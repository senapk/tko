from typing import Any, Dict
import os
import tempfile
from ..util.remote import RemoteCfg, Absolute


class RepSettings:
    __expanded = "expanded"
    __new_items = "new_items"
    __tasks = "tasks"
    __flags = "flags"
    __lang = "lang"

    defaults = {
        __expanded: [],
        __tasks: {},
        __flags: {},
        __new_items: [],
        __lang: ""
    }

    def get_expanded(self) -> list:
        return self.__get(RepSettings.__expanded)
    
    def get_new_items(self) -> list:
        return self.__get(RepSettings.__new_items)
    
    def get_tasks(self) -> Dict[str, Any]:
        return self.__get(RepSettings.__tasks)
    
    def get_flags(self) -> Dict[str, Any]:
        return self.__get(RepSettings.__flags)
    
    def get_lang(self) -> str:
        return self.__get(RepSettings.__lang)
    
    def set_expanded(self, value: list):
        return self.__set(RepSettings.__expanded, value)
    
    def set_new_items(self, value: list):
        return self.__set(RepSettings.__new_items, value)
    
    def set_tasks(self, value: Dict[str, Any]):
        return self.__set(RepSettings.__tasks, value)
    
    def set_flags(self, value: Dict[str, Any]):
        return self.__set(RepSettings.__flags, value)
    
    def set_lang(self, value: str):
        return self.__set(RepSettings.__lang, value)

    def __init__(self, file: str = ""):
        self.url: str = ""
        self.file: str = ""
        self.data: Dict[str, Any] = {}
        if file != "":
            self.file = os.path.abspath(file)

    def __get(self, key: str) -> Any:
        if key not in self.defaults:
            raise ValueError(f"Key {key} not found in RepSettings")
        value = self.data.get(key, RepSettings.defaults[key])
        if type(value) != type(RepSettings.defaults[key]):
            return RepSettings.defaults[key]
        return value

    def __set(self, key: str, value: Any):
        self.data[key] = value
        return self

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

    def set_url(self, url: str):
        self.url = url
        return self
    
    def load_defaults(self):
        for key in RepSettings.defaults:
            self.data[key] = RepSettings.defaults[key]
        return self

    def to_dict(self):
        return {
            "url": self.url,
            "file": self.file,
            "data": self.data
        }

    def from_dict(self, data: Dict[str, Any]):
        self.url = data.get("url", "")
        self.file = data.get("file", "")
        self.data = data.get("data", {})
        return self

    def __str__(self) -> str:
        return (
            f"url: {self.url}\n"
            f"file: {self.file}\n"
            f"data: {self.data}\n"
        )
