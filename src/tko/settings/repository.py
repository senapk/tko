from typing import Any, Dict, List
import os
import json
import urllib
from tko.util.remote_url import RemoteUrl, Absolute
from tko.game.game import Game
from tko.game.task import Task
from tko.util.decoder import Decoder

available_languages = ["c", "cpp", "py", "ts", "java", "go", "yaml"]

class Repository:
    CFG_FILE = "repository.json"
    LOG_FILE = "history.csv"
    DAILY_FILE = "daily.json"
    INDEX_FILE = "Readme.md"
    REMOTE_TASK_FOLDER = "remote"
    CONFIG_FOLDER = ".tko"

    def __init__(self, folder: str):
        self.folder: str = folder
        self.data: Dict[str, Any] = {}
        self.game = Game()

    @staticmethod
    def rec_search_for_repo(folder: str) -> str:
        if os.path.exists(os.path.join(folder, Repository.CONFIG_FOLDER, Repository.CFG_FILE)):
            return folder
        new_folder = os.path.dirname(folder)
        if new_folder == folder:
            return ""
        return Repository.rec_search_for_repo(new_folder)

    def get_remote_task_folder(self, label: str) -> str:
        return os.path.abspath(os.path.join(self.folder, Repository.REMOTE_TASK_FOLDER, label))

    def is_local_dir(self, path):
        rep_dir = self.get_rep_dir()
        path = os.path.abspath(path)
        return os.path.commonpath([rep_dir, path]) == rep_dir

    @staticmethod
    def is_web_link(link: str) -> bool:
        return link.startswith("http:") or link.startswith("https:")

    def set_task_folder(self, task: Task):
        if not task.is_downloadable():
            if not self.is_web_link(task.link):
                task_dir = os.path.abspath(os.path.dirname(task.link))
                task.set_folder(task_dir)
        else: # downloadable task
            task_dir = self.get_remote_task_folder(task.key)
            task.set_folder(task_dir)

    def load_game(self):
        self.game.parse_file(self.load_index_or_cache())
        for task in self.game.tasks.values():
            self.set_task_folder(task)
        return self

    def get_repository_file(self) -> str:
        return os.path.abspath(os.path.join(self.folder, Repository.CONFIG_FOLDER, Repository.CFG_FILE))
    
    def get_history_file(self) -> str:
        return os.path.abspath(os.path.join(self.folder, Repository.CONFIG_FOLDER, Repository.LOG_FILE))
    
    def get_daily_file(self) -> str:
        return os.path.abspath(os.path.join(self.folder, Repository.CONFIG_FOLDER, Repository.DAILY_FILE))
    
    def get_default_readme_path(self) -> str:
        return os.path.abspath(os.path.join(self.folder, Repository.INDEX_FILE))

    def get_rep_dir(self) -> str:
        return os.path.abspath(self.folder)

    def load_index_or_cache(self) -> str:
        file: str = self.get_local_file()
        remote: str = self.get_remote_source()
        # arquivo existe e é local
        if file != "" and os.path.exists(file) and remote == "":
            return file
        
        if not remote.startswith("http:)") and not remote.startswith("https:"):
            return remote

        # arquivo não existe e é remoto
        if remote != "" and (file == "" or not os.path.exists(file)):
            cache_file = self.get_default_readme_path()
            os.makedirs(self.folder, exist_ok=True)
            ru = RemoteUrl(remote)
            try:
                ru.download_absolute_to(cache_file)
            except urllib.error.URLError:
                print("Não foi possível baixar o arquivo do repositório")
                if os.path.exists(cache_file):
                    print("Usando arquivo do cache")
                else:
                    raise Warning("fail: Arquivo do cache não encontrado")
            return cache_file

        raise Warning("fail: arquivo não encontrado ou configurações inválidas para o repositório")

    __version = "version"
    __remote_url = "remote"  #remote url
    __local_file = "local"  #local file
    __expanded = "expanded"
    __new_items = "new_items"
    __tasks = "tasks"
    __flags = "flags"
    __lang = "lang"
    __selected = "index"

    defaults = {
        __version: "0.0.0",
        __remote_url: "",
        __local_file: "",
        __expanded: [],
        __tasks: {},
        __flags: {},
        __new_items: [],
        __lang: "",
        __selected: ""
    }

    def get_version(self) -> str:
        return self.__get(Repository.__version)
    
    def set_version(self, value: str):
        self.__set(Repository.__version, value)
        return self

    def get_local_file(self) -> str:
        return self.__get(Repository.__local_file)
    
    def set_local_file(self, value: str):
        self.__set(Repository.__local_file, value)
        return self

    def get_remote_source(self) -> str:
        return self.__get(Repository.__remote_url)
    
    def set_remote_source(self, value: str):
        self.__set(Repository.__remote_url, value)
        return self

    def get_selected(self) -> str:
        return self.__get(Repository.__selected)

    def get_expanded(self) -> List[str]:
        return self.__get(Repository.__expanded)

    def get_new_items(self) -> List[str]:
        return self.__get(Repository.__new_items)
    
    def get_tasks(self) -> Dict[str, Any]:
        return self.__get(Repository.__tasks)
    
    def get_flags(self) -> Dict[str, Any]:
        return self.__get(Repository.__flags)
    
    def get_lang(self) -> str:
        return self.__get(Repository.__lang)

    def set_expanded(self, value: List[str]):
        return self.__set(Repository.__expanded, value)
    
    def set_new_items(self, value: List[str]):
        return self.__set(Repository.__new_items, value)
    
    def set_tasks(self, value: Dict[str, str]):
        self.__set(Repository.__tasks, value)
        return self
    
    def set_flags(self, value: Dict[str, Any]):
        self.__set(Repository.__flags, value)
        return self
    
    def set_lang(self, value: str):
        self.__set(Repository.__lang, value)
        return self
    
    def set_selected(self, value: str):
        self.__set(Repository.__selected, value)
        return self

    def __get(self, key: str) -> Any:
        if key not in self.defaults:
            raise ValueError(f"Key {key} not found in RepSettings")
        value = self.data.get(key, Repository.defaults[key])
        if type(value) != type(Repository.defaults[key]):
            return Repository.defaults[key]
        return value

    def __set(self, key: str, value: Any):
        self.data[key] = value
        return self

    def create_empty_config_file(self, point_to_local_readme: bool = False):
        if point_to_local_readme:
            self.set_local_file(self.get_default_readme_path())
        self.save_data_to_config_file()
        return self

    def has_local_config_file(self) -> bool:
        return os.path.exists(self.get_repository_file())

    def load_data_from_config_file(self):
        encoding = Decoder.get_encoding(self.get_repository_file())
        with open(self.get_repository_file(), encoding=encoding) as f:
            self.data = json.load(f)
        return self

    def save_data_to_config_file(self):
        json_file = self.get_repository_file()
        if not os.path.exists(os.path.dirname(json_file)):
            os.makedirs(os.path.dirname(json_file))
        # filter keys that are not in defaults
        for key in list(self.data.keys()):
            if key not in Repository.defaults:
                del self.data[key]

        for key in Repository.defaults:
            if key not in self.data:
                self.data[key] = Repository.defaults[key]

        with open(json_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data, indent=4))
        return self

    def __str__(self) -> str:
        return ( f"data: {self.data}\n" )
