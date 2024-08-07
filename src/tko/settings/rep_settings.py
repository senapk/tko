from typing import Any, Dict
import os
import json
import tempfile
from ..util.remote import RemoteCfg, Absolute


class RepSource:
    def __init__(self, file: str = "", url: str = ""):
        self.file: str = ""
        if file != "":
            self.file = os.path.abspath(file)        
        self.url: str = url

    def set_file(self, file: str):
        self.file = os.path.abspath(file)
        return self

    def set_url(self, url: str):
        self.url = url
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "url": self.url
        }

    def from_dict(self, data: Dict[str, Any]):
        self.file = data.get("file", "")
        self.url = data.get("url", "")
        return self    

class RepData:

    def __init__(self, json_file: str = ""):
        self.json_file: str = json_file
        self.data: Dict[str, Any] = {}

    __expanded = "expanded"
    __new_items = "new_items"
    __tasks = "tasks"
    __flags = "flags"
    __lang = "lang"
    __index = "index"

    defaults = {
        __expanded: [],
        __tasks: {},
        __flags: {},
        __new_items: [],
        __lang: "",
        __index: 0
    }

    def get_index(self) -> int:
        return self.__get(RepData.__index)

    def get_expanded(self) -> list:
        return self.__get(RepData.__expanded)
    
    def get_new_items(self) -> list:
        return self.__get(RepData.__new_items)
    
    def get_tasks(self) -> Dict[str, Any]:
        return self.__get(RepData.__tasks)
    
    def get_flags(self) -> Dict[str, Any]:
        return self.__get(RepData.__flags)
    
    def get_lang(self) -> str:
        return self.__get(RepData.__lang)
    
    def set_expanded(self, value: list):
        return self.__set(RepData.__expanded, value)
    
    def set_new_items(self, value: list):
        return self.__set(RepData.__new_items, value)
    
    def set_tasks(self, value: Dict[str, Any]):
        return self.__set(RepData.__tasks, value)
    
    def set_flags(self, value: Dict[str, Any]):
        return self.__set(RepData.__flags, value)
    
    def set_lang(self, value: str):
        return self.__set(RepData.__lang, value)
    
    def set_index(self, value: int):
        return self.__set(RepData.__index, value)

    def __get(self, key: str) -> Any:
        if key not in self.defaults:
            raise ValueError(f"Key {key} not found in RepSettings")
        value = self.data.get(key, RepData.defaults[key])
        if type(value) != type(RepData.defaults[key]):
            return RepData.defaults[key]
        return value

    def __set(self, key: str, value: Any):
        self.data[key] = value
        return self

    def load_defaults(self):
        for key in RepData.defaults:
            self.data[key] = RepData.defaults[key]
        return self

    def load_data_from_json(self):
        with open(self.json_file, encoding="utf-8") as f:
            self.data = json.load(f)
        return self


    def save_data_to_json(self):
        if not os.path.exists(os.path.dirname(self.json_file)):
            os.makedirs(os.path.dirname(self.json_file))
        with open(self.json_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data, indent=4))
        return self

    def __str__(self) -> str:
        return (
            f"data: {self.data}\n"
        )
