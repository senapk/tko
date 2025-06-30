from typing import Any
import os
import urllib
from tko.util.remote_url import RemoteUrl
from tko.game.game import Game
from tko.util.decoder import Decoder
from tko.util.text import Text
from tko.logger.logger import Logger
import yaml # type: ignore
from tko.settings.rep_paths import RepPaths

def remove_git_merge_tags(lines: list[str]) -> list[str]:
    # remove lines with <<<<<<<, =======, >>>>>>>>
    filtered_lines: list[str] = []
    for line in lines:
        if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
            continue
        filtered_lines.append(line)
    return filtered_lines
class Repository:


    def __init__(self, folder: str):
        rep_folder: str = folder
        recursive_folder = RepPaths.rec_search_for_repo(folder)
        if recursive_folder != "":
            rep_folder = recursive_folder
        self.paths = RepPaths(rep_folder)
        self.data: dict[str, Any] = {}
        self.game = Game()
        self.logger: Logger = Logger(rep_folder)

    def found(self):
        return os.path.isfile(self.paths.get_config_file())

    def is_local_dir(self, path: str) -> bool:
        rep_dir = self.paths.get_rep_dir()
        path = os.path.abspath(path)
        return os.path.commonpath([rep_dir, path]) == rep_dir

    @staticmethod
    def is_web_link(link: str) -> bool:
        return link.startswith("http:") or link.startswith("https:")

    def load_game(self):
        if self.data == {}:
            self.load_config()
        database_folder = os.path.join(self.paths.root_folder, self.get_database_folder())
        cache_or_index = self.load_index_or_cache()
        self.game.parse_file_and_folder(cache_or_index, database_folder, self.get_lang())
        self.__load_tasks_from_rep_into_game()
        return self
    
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
    
    
    def __load_tasks_from_rep_into_game(self):
        # load tasks from repository.yaml into game
        tasks = self.get_tasks()
        for key, serial in tasks.items():
            if key in self.game.tasks:
                self.game.tasks[key].load_from_db(serial)

    def get_task_folder_for_label(self, label: str) -> str:
        return os.path.abspath(os.path.join(self.paths.root_folder, self.get_database_folder(), label))


    def __load_local_file(self, source: str) -> str:
        # test if file is inside or outside the repository
        source_full = os.path.join(self.paths.get_config_folder(), source)
        if not os.path.exists(source_full):
            raise Warning(Text.format("{r}: Arquivo fonte do repositório {y} não foi encontrado", "Erro", source))
        return source_full

    def __is_remote_source(self) -> bool:
        source = self.get_rep_source()
        return source.startswith("http:") or source.startswith("https:")
    
    def down_source_from_remote_url(self):
        source = self.get_rep_source()
        cache_file = self.paths.get_default_readme_path()
        os.makedirs(self.paths.root_folder, exist_ok=True)
        ru = RemoteUrl(source)
        try:
            ru.download_absolute_to(cache_file)
        except urllib.error.URLError: # type: ignore
            print("Não foi possível baixar o arquivo do repositório")
            if os.path.exists(cache_file):
                print("Usando arquivo do cache")
            else:
                raise Warning("fail: Arquivo do cache não encontrado")
        return cache_file

    def load_index_or_cache(self) -> str:
        source = self.get_rep_source()
        if source == "":
            return ""

        if self.__is_remote_source():
            return self.down_source_from_remote_url()
        return self.__load_local_file(source)

    __version = "version"
    __actual_version = "0.0.1"
    __source = "remote"  #remote url or local file or remote file
    __expanded = "expanded"
    __tasks = "tasks"
    __flags = "flags"
    __lang = "lang"
    __selected = "index"
    __database = "database"

    defaults: dict[str, Any] = {
        __version: __actual_version,
        __database: "database",
        __source: "",
        __expanded: [],
        __tasks: {},
        __flags: {},
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

    def get_expanded(self) -> list[str]:
        return self.__get(Repository.__expanded)

    def get_tasks(self) -> dict[str, Any]:
        return self.__get(Repository.__tasks)
    
    def get_flags(self) -> dict[str, Any]:
        return self.__get(Repository.__flags)
    
    def get_lang(self) -> str:
        return self.__get(Repository.__lang)

    def set_expanded(self, value: list[str]):
        return self.__set(Repository.__expanded, value)
    
    def set_tasks(self, value: dict[str, str]):
        self.__set(Repository.__tasks, value)
        return self
    
    def set_flags(self, value: dict[str, Any]):
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
            self.set_rep_source(self.paths.get_default_readme_path())
        self.save_config()
        return self

    # config
    def load_config(self):
        encoding = Decoder.get_encoding(self.paths.get_config_file())
        try:
            with open(self.paths.get_config_file(), encoding=encoding) as f:
                lines = f.readlines()
                lines = remove_git_merge_tags(lines)
                self.data = yaml.safe_load("\n".join(lines))
            if self.data is None or not isinstance(self.data, dict) or len(self.data) == 0: # type: ignore
                with open(self.paths.get_config_backup_file(), "r", encoding=encoding) as f:
                    lines = f.readlines()
                    lines = remove_git_merge_tags(lines)
                    self.data = yaml.safe_load("\n".join(lines))
            if self.data is None or not isinstance(self.data, dict) or len(self.data) == 0: # type: ignore
                raise FileNotFoundError(f"Arquivo de configuração vazio: {self.paths.get_config_file()}")
        except:
            raise Warning(Text.format("O arquivo de configuração do repositório {y} está {r}.\nAbra e corrija o conteúdo ou crie um novo.", self.paths.get_config_file(), "corrompido"))
        return self

    def save_config(self):
        self.set_version(self.__actual_version)
        yaml_file = self.paths.get_config_file()
        if not os.path.exists(os.path.dirname(yaml_file)):
            os.makedirs(os.path.dirname(yaml_file))
        # filter keys that are not in defaults
        for key in list(self.data.keys()):
            if key not in Repository.defaults:
                del self.data[key]

        for key in Repository.defaults:
            if key not in self.data:
                self.data[key] = Repository.defaults[key]
        yaml_file_new = yaml_file + ".new"
        yaml_file_bkp = yaml_file + ".backup"
        with open(yaml_file_new, "w", encoding="utf-8") as f:
            yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        # copy file from yaml_file to yaml_file.backup
        try:
            Repository.rename_file(yaml_file, yaml_file_bkp)
        except:
            pass
        Repository.rename_file(yaml_file_new, yaml_file)
        return self

    def __str__(self) -> str:
        return f"data: {self.data}\n"

    @staticmethod
    def rename_file(old_name: str, new_name: str):
        if os.path.exists(old_name):
            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(old_name, new_name)
        else:
            raise Warning(Text.format("O arquivo {y} não foi encontrado", old_name))