from typing import Any, Dict, List
import os
import json
import urllib
from tko.util.remote_url import RemoteUrl, Absolute
from tko.game.game import Game
from tko.game.task import Task
from tko.util.decoder import Decoder
from tko.util.text import Text
import yaml # type: ignore

available_languages = ["c", "cpp", "py", "ts", "java", "go", "yaml"]

class Repository:
    OLD_CFG_FILE = "repository.json" # reprecated
    NEW_CFG_FILE = "repository.yaml"
    LOG_FILE = "history.csv"
    DAILY_FILE = "daily.yaml"
    INDEX_FILE = "Readme.md"
    TRACK_FOLDER = "track"
    CONFIG_FOLDER = ".tko"

    def __init__(self, folder: str):
        self.root_folder: str = folder
        rec_folder = Repository.rec_search_for_repo(folder)
        if rec_folder != "":
            self.root_folder = rec_folder

        self.data: Dict[str, Any] = {}
        self.game = Game()
        self.upgrade_version()

    def upgrade_version(self):
        return self

    @staticmethod
    def rec_search_for_repo(folder: str) -> str:
        folder = os.path.abspath(folder)
        if os.path.exists(os.path.join(folder, Repository.CONFIG_FOLDER, Repository.NEW_CFG_FILE)):
            return folder
        if os.path.exists(os.path.join(folder, Repository.CONFIG_FOLDER, Repository.OLD_CFG_FILE)):
            return folder
        new_folder = os.path.dirname(folder)
        if new_folder == folder: # não encontrou, não tem mais como subir
            return ""
        return Repository.rec_search_for_repo(new_folder)

    def get_key_from_task_folder(self, folder: str) -> str:
        label = os.path.basename(folder)
        task_folder = self.get_task_folder_for_label(label)
        if task_folder == folder:
            return label
        return ""

    def is_task_folder(self, folder: str) -> bool:
        label = os.path.basename(folder)
        task_folder = self.get_task_folder_for_label(label)
        return task_folder == folder

    def get_track_task_folder(self, label: str) -> str:
        return os.path.abspath(os.path.join(self.root_folder, Repository.CONFIG_FOLDER, Repository.TRACK_FOLDER, label))

    def get_task_folder_for_label(self, label: str) -> str:
        return os.path.abspath(os.path.join(self.root_folder, self.get_database_folder(), label))

    def is_local_dir(self, path):
        rep_dir = self.get_rep_dir()
        path = os.path.abspath(path)
        return os.path.commonpath([rep_dir, path]) == rep_dir

    @staticmethod
    def is_web_link(link: str) -> bool:
        return link.startswith("http:") or link.startswith("https:")

    def load_game(self):
        if self.data == {}:
            self.load_config()
        database_folder = os.path.join(self.root_folder, self.get_database_folder())
        cache_or_index = self.load_index_or_cache()
        self.game.parse_file_and_folder(cache_or_index, database_folder)
        self.__load_tasks_from_rep_into_game()
        return self
    
    def __load_tasks_from_rep_into_game(self):
        tasks = self.get_tasks()
        for key, serial in tasks.items():
            if key in self.game.tasks:
                self.game.tasks[key].load_from_db(serial)

    def get_old_config_file(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, Repository.CONFIG_FOLDER, Repository.OLD_CFG_FILE))

    def get_config_file(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, Repository.CONFIG_FOLDER, Repository.NEW_CFG_FILE))
    
    def get_history_file(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, Repository.CONFIG_FOLDER, Repository.LOG_FILE))
    
    def get_daily_file(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, Repository.CONFIG_FOLDER, Repository.DAILY_FILE))
    
    def get_default_readme_path(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, Repository.INDEX_FILE))

    def get_rep_dir(self) -> str:
        return os.path.abspath(self.root_folder)

    def __load_local_file(self, source: str) -> str:
        # test if file is inside or outside the repository
        source = os.path.abspath(os.path.join(self.root_folder, self.CONFIG_FOLDER, source))
        if not os.path.exists(source):
            raise Warning(Text.format("{r}: Arquivo fonte do repositório {y} não foi encontrado", "Erro", source))
        return source

    def __is_remote_source(self) -> bool:
        source = self.get_rep_source()
        return source.startswith("http:") or source.startswith("https:")
    
    def down_source_from_remote_url(self):
        source = self.get_rep_source()
        cache_file = self.get_default_readme_path()
        os.makedirs(self.root_folder, exist_ok=True)
        ru = RemoteUrl(source)
        try:
            ru.download_absolute_to(cache_file)
        except urllib.error.URLError:
            print("Não foi possível baixar o arquivo do repositório")
            if os.path.exists(cache_file):
                print("Usando arquivo do cache")
            else:
                raise Warning("fail: Arquivo do cache não encontrado")
        return cache_file

    def load_index_or_cache(self) -> str:
        source = self.get_rep_source()

        if self.__is_remote_source():
            return self.down_source_from_remote_url()
        return self.__load_local_file(source)

    __version = "version"
    __actual_version = "0.0.1"
    __source = "remote"  #remote url or local file or remote file
    __expanded = "expanded"
    __new_items = "new_items"
    __tasks = "tasks"
    __flags = "flags"
    __lang = "lang"
    __selected = "index"
    __database = "database"

    defaults = {
        __version: __actual_version,
        __database: "database",
        __source: "",
        __expanded: [],
        __tasks: {},
        __flags: {},
        __new_items: [],
        __lang: "",
        __selected: ""
    }

    def get_database_folder(self) -> str:
        return self.__get(Repository.__database)

    def set_database_folder(self, value: str):
        self.__set(Repository.__database, value)
        return self

    def get_version(self) -> str:
        return self.__get(Repository.__version)
    
    def set_version(self, value: str):
        self.__set(Repository.__version, value)
        return self

    def get_rep_source(self) -> str:
        return self.__get(Repository.__source)
    
    def set_rep_source(self, value: str):
        self.__set(Repository.__source, value)
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
            self.set_rep_source(self.get_default_readme_path())
        self.save_config()
        return self

    def has_local_config_file(self) -> bool:
        return os.path.exists(self.get_config_file()) or os.path.exists(self.get_old_config_file())

    def load_config(self):
        encoding = Decoder.get_encoding(self.get_config_file())
        if os.path.exists(self.get_old_config_file()):
            try:
                with open(self.get_old_config_file(), encoding=encoding) as f:
                    self.data = json.load(f)
                with open(self.get_config_file(), "w", encoding="utf-8") as f:
                    yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                os.remove(self.get_old_config_file())
            except:
                pass
        try:
            with open(self.get_config_file(), encoding=encoding) as f:
                self.data = yaml.safe_load(f)
        except:
            raise Warning(Text.format("O arquivo de configuração do repositório {y} está {r}.\nAbra e corrija o conteúdo ou crie um novo.", self.get_config_file(), "corrompido"))
        return self

    def save_config(self):
        self.set_version(self.__actual_version)
        json_file = self.get_config_file()
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
            # f.write(json.dumps(self.data, indent=4))
            yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return self

    def __str__(self) -> str:
        return ( f"data: {self.data}\n" )
