from typing import Any, Dict, List
import os
import json
import urllib
from ..util.remote import RemoteCfg, Absolute

languages_avaliable = ["c", "cpp", "py", "ts", "js", "java", "go"]

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

    def get_file_or_cache(self, rep_dir: str) -> str:
        # arquivo existe e é local
        if self.file != "" and os.path.exists(self.file) and self.url == "":
            return self.file

        # arquivo não existe e é remoto
        if self.url != "" and (self.file == "" or not os.path.exists(self.file)):
            cache_file = os.path.join(rep_dir, ".cache.md")
            os.makedirs(rep_dir, exist_ok=True)
            cfg = RemoteCfg(self.url)
            try:
                cfg.download_absolute(cache_file)
            except urllib.error.URLError:
                print("fail: Não foi possível baixar o arquivo do repositório")
                if os.path.exists(cache_file):
                    print("Usando arquivo do cache")
                else:
                    raise Warning("fail: Arquivo do cache não encontrado")
            return cache_file

        raise ValueError("fail: arquivo não encontrado ou configurações inválidas para o repositório")

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

    def __init__(self, rootdir: str, alias: str, json_file: str = ""):
        self.json_file: str = json_file
        self.data: Dict[str, Any] = {}
        self.rootdir = rootdir
        self.alias = alias

    def get_rootdir(self) -> str:
        return self.rootdir

    def get_rep_dir(self) -> str:
        return os.path.join(self.rootdir, self.alias)

    __expanded = "expanded"
    __new_items = "new_items"
    __tasks = "tasks"
    __flags = "flags"
    __lang = "lang"
    __selected = "index"

    defaults = {
        __expanded: [],
        __tasks: {},
        __flags: {},
        __new_items: [],
        __lang: "",
        __selected: ""
    }

    def get_selected(self) -> str:
        return self.__get(RepData.__selected)

    def get_expanded(self) -> List[str]:
        return self.__get(RepData.__expanded)

    def get_new_items(self) -> List[str]:
        return self.__get(RepData.__new_items)
    
    def get_tasks(self) -> Dict[str, Any]:
        return self.__get(RepData.__tasks)
    
    def get_flags(self) -> Dict[str, Any]:
        return self.__get(RepData.__flags)
    
    def get_lang(self) -> str:
        return self.__get(RepData.__lang)

    def set_expanded(self, value: List[str]):
        return self.__set(RepData.__expanded, value)
    
    def set_new_items(self, value: List[str]):
        return self.__set(RepData.__new_items, value)
    
    def set_tasks(self, value: Dict[str, str]):
        return self.__set(RepData.__tasks, value)
    
    def set_flags(self, value: Dict[str, Any]):
        return self.__set(RepData.__flags, value)
    
    def set_lang(self, value: str):
        return self.__set(RepData.__lang, value)
    
    def set_selected(self, value: str):
        return self.__set(RepData.__selected, value)

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
        # filter keys that are not in defaults
        for key in list(self.data.keys()):
            if key not in RepData.defaults:
                del self.data[key]

        with open(self.json_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data, indent=4))
        return self

    def __str__(self) -> str:
        return ( f"data: {self.data}\n" )
