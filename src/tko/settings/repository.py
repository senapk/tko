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
from icecream import ic # type: ignore

def remove_git_merge_tags(lines: list[str]) -> list[str]:
    # remove lines with <<<<<<<, =======, >>>>>>>>
    filtered_lines: list[str] = []
    for line in lines:
        if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
            continue
        filtered_lines.append(line)
    return filtered_lines

class Source:
    def __init__(self, alias: str = "", link: str = "", filters: list[str] | None = None):
        self.alias = alias
        self.link = link
        self.last_cache: str = ""
        self.filter: list[str] = [] if filters is None else filters
    
    def set_alias(self, alias: str):
        self.alias = alias
        return self

    def set_link(self, link: str):
        self.link = link
        return self
    
    def set_last_cache(self, last_cache: str):
        self.last_cache = last_cache
        return self
    
    def set_filter(self, filter: list[str]):
        self.filter = filter
        return self

    def load_from_dict(self, data: dict[str, Any]):
        if "alias" in data and isinstance(data["alias"], str):
            self.alias = data["alias"]
        if "link" in data and isinstance(data["link"], str):
            self.link = data["link"]
        if "last_cache" in data and isinstance(data["last_cache"], str):
            self.last_cache = data["last_cache"]
        if "filter" in data and isinstance(data["filter"], list):
            self.filter = data["filter"]
        return self
    
    def save_to_dict(self) -> dict[str, Any]:
        return {
            "alias": self.alias,
            "link": self.link,
            "last_cache": self.last_cache,
            "filter": self.filter
        }

class RepData:
    def __init__(self):
        self.version: str = ""
        self.sources: list[Source] = []
        self.expanded: list[str] = []
        self.tasks: dict[str, Any] = {}
        self.flags: dict[str, Any] = {}
        self.lang: str = ""
        self.selected: str = ""
        self.database: str = "database"

    def _safe_load(self, data: dict[str, Any], key: str, target_type: type, default_value: Any = None):
        """Helper method to safely load a value from a dictionary."""
        if key in data and isinstance(data[key], target_type):
            return data[key]
        return default_value

    def load_from_dict(self, data: dict[str, Any]):
        try:
            # Load simple fields
            self.version = self._safe_load(data, "version", str, self.version)
            self.expanded = self._safe_load(data, "expanded", list, self.expanded)
            self.tasks = self._safe_load(data, "tasks", dict, self.tasks)
            self.flags = self._safe_load(data, "flags", dict, self.flags)
            self.lang = self._safe_load(data, "lang", str, self.lang)
            self.selected = self._safe_load(data, "selected", str, self.selected)
            self.database = self._safe_load(data, "database", str, self.database)

            # Load the 'source' field with specific validation
            if "sources" in data:
                source_data: list[dict[str, Any]] = data["sources"]
                if isinstance(source_data, list): # type: ignore
                    self.sources = [Source().load_from_dict(x) for x in source_data]
                else:
                    raise TypeError("The 'sources' field must be a list.")

        except (KeyError, TypeError) as e:
            print(f"Error loading data from dictionary: {e}")
            # Optionally, you can re-raise the exception or handle it differently
            # raise ValueError("Malformed data for RepData") from e

    def save_to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "sources": [x.save_to_dict() for x in self.sources],
            "expanded": self.expanded,
            "tasks": self.tasks,
            "flags": self.flags,
            "lang": self.lang,
            "selected": self.selected,
            "database": self.database
        }



class Repository:

    def __init__(self, folder: str):
        rep_folder: str = folder
        recursive_folder = RepPaths.rec_search_for_repo(folder)
        if recursive_folder != "":
            rep_folder = recursive_folder
        self.paths = RepPaths(rep_folder)
        self.data: RepData = RepData()
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
        if self.data.database == "":
            self.load_config()
        database_folder = os.path.join(self.paths.root_folder, self.data.database)
        for source in  self.data.sources:
            cache_or_index = self.load_index_or_cache(source)
            self.game.parse_file_and_folder(cache_or_index, database_folder, self.data.lang, source.filter)
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
        tasks = self.data.tasks
        for key, serial in tasks.items():
            if key in self.game.tasks:
                self.game.tasks[key].load_from_db(serial)

    def get_task_folder_for_label(self, label: str) -> str:
        return os.path.abspath(os.path.join(self.paths.root_folder, self.data.database, label))


    def __load_local_file(self, source: Source) -> str:
        # test if file is inside or outside the repository
        source_full = os.path.join(self.paths.get_config_folder(), source.link)
        if not os.path.exists(source_full):
            raise Warning(Text.format("{r}: Arquivo fonte do repositório {y} não foi encontrado", "Erro", source))
        return source_full

    def __is_remote_source(self, source: Source) -> bool:
        return source.link.startswith("http:") or source.link.startswith("https:")

    def down_source_from_remote_url(self, source: Source):
        cache_file = self.paths.get_default_readme_path()
        os.makedirs(self.paths.root_folder, exist_ok=True)
        ru = RemoteUrl(source.link)
        try:
            ru.download_absolute_to(cache_file)
        except urllib.error.URLError: # type: ignore
            print("Não foi possível baixar o arquivo do repositório")
            if os.path.exists(cache_file):
                print("Usando arquivo do cache")
            else:
                raise Warning("fail: Arquivo do cache não encontrado")
        return cache_file

    def load_index_or_cache(self, source: Source) -> str:
        if source.link == "":
            return ""

        if self.__is_remote_source(source):
            return self.down_source_from_remote_url(source)
        return self.__load_local_file(source)


    def create_empty_config_file(self, point_to_local_readme: bool = False):
        if point_to_local_readme:
            self.data.sources.append(Source("local",self.paths.get_default_readme_path()))
        self.save_config()
        return self

    # config
    def load_config(self):
        encoding = Decoder.get_encoding(self.paths.get_config_file())
        local_data: dict[str, Any] = {}
        try:
            with open(self.paths.get_config_file(), encoding=encoding) as f:
                lines = f.readlines()
                lines = remove_git_merge_tags(lines)
                local_data = yaml.safe_load("\n".join(lines))
            if local_data is None or not isinstance(self.data, dict) or len(self.data) == 0: # type: ignore
                with open(self.paths.get_config_backup_file(), "r", encoding=encoding) as f:
                    lines = f.readlines()
                    lines = remove_git_merge_tags(lines)
                    local_data = yaml.safe_load("\n".join(lines))
            if local_data is None or not isinstance(local_data, dict) or len(local_data) == 0: # type: ignore
                raise FileNotFoundError(f"Arquivo de configuração vazio: {self.paths.get_config_file()}")
        except:
            raise Warning(Text.format("O arquivo de configuração do repositório {y} está {r}.\nAbra e corrija o conteúdo ou crie um novo.", self.paths.get_config_file(), "corrompido"))
        if local_data["version"] == "0.0.1":
            local_data["sources"] = [Source("legacy", local_data["remote"], local_data["filter"]).save_to_dict()]
        self.data.load_from_dict(local_data)

        return self

    def save_config(self):
        self.data.version = "0.2"
        yaml_file = self.paths.get_config_file()
        if not os.path.exists(os.path.dirname(yaml_file)):
            os.makedirs(os.path.dirname(yaml_file))
        yaml_file_new = yaml_file + ".new"
        yaml_file_bkp = yaml_file + ".backup"
        with open(yaml_file_new, "w", encoding="utf-8") as f:
            yaml.dump(self.data.save_to_dict(), f, default_flow_style=False, allow_unicode=True, sort_keys=False)
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