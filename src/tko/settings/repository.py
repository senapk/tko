from typing import Any
import os
import urllib
from tko.settings.rep_data import RepData
from tko.settings.rep_source import RepSource
from tko.util.remote_url import RemoteUrl
from tko.game.game import Game
from tko.util.decoder import Decoder
from tko.util.text import Text
from tko.logger.logger import Logger
import yaml # type: ignore
from tko.settings.rep_paths import RepPaths
from icecream import ic # type: ignore
from tko.logger.delta import Delta
from tko.settings.legacy import Legacy

def remove_git_merge_tags(lines: list[str]) -> list[str]:
    # remove lines with <<<<<<<, =======, >>>>>>>>
    filtered_lines: list[str] = []
    for line in lines:
        if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
            continue
        filtered_lines.append(line)
    return filtered_lines

class Repository:
    cache_time_for_remote_source = 3600 # seconds

    def __init__(self, folder: str, force_update: bool = False):
        rep_folder: str = folder
        recursive_folder = RepPaths.rec_search_for_repo(folder)
        if recursive_folder != "":
            rep_folder = recursive_folder
        self.paths = RepPaths(rep_folder)
        self.data: RepData = RepData()
        self.game = Game()
        self.logger: Logger = Logger(rep_folder) 
        self.force_update: bool = force_update

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
        if not self.data.get_sources():
            self.load_config()
        for source in self.data.get_sources():
            self.update_cache_path(source)
        sources: list[RepSource] = self.data.get_sources()
        self.game.load_sources(sources, self.data.lang)
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
        parts: list[str] = label.split("@")
        source = ""
        if len(parts) > 1:
            source = parts[0]
            label = parts[1]
        return os.path.abspath(os.path.join(self.paths.root_folder, source, label))


    def __is_remote_source(self, source: RepSource) -> bool:
        return source.link.startswith("http:") or source.link.startswith("https:")

    def down_source_from_remote_url(self, source: RepSource) -> None:
        cache_file = source.get_default_cache_path()
        os.makedirs(self.paths.get_cache_folder(), exist_ok=True)
        ru = RemoteUrl(source.link)
        try:
            ru.download_absolute_to(cache_file)
        except urllib.error.URLError: # type: ignore
            print(f"Não foi possível baixar o arquivo do repositório alias:{source.database}, link:{source.link}")
            if os.path.exists(cache_file):
                print("Usando arquivo do cache")
            else:
                raise Warning("fail: Arquivo do cache não encontrado")

    def update_cache_path(self, source: RepSource) -> None:
        if source.link == "":
            source.target_path = ""
            return

        if self.__is_remote_source(source):
            now_str, now_dt = Delta.now()
            # verify if cache file exists and is less than 1 hour old
            cache_file = source.get_default_cache_path()
            source.target_path = cache_file
            if not self.force_update and os.path.isfile(cache_file) and source.cache_timestamp != "":
                last_dt = Delta.decode_format(source.cache_timestamp)
                if (now_dt - last_dt).total_seconds() < Repository.cache_time_for_remote_source:
                    time_missing = Repository.cache_time_for_remote_source - (now_dt - last_dt).total_seconds()
                    r = int(time_missing / 60)
                    print(f"Usando cache do repositório {source.database} ({source.link}), próxima atualização em {r} minutos")
                    return

            self.down_source_from_remote_url(source)
            source.cache_timestamp = now_str
            return
        
        # local source
        if os.path.abspath(source.link) == source.link: # absolute path
            source.target_path = source.link
        else: # relative path
            source.target_path = os.path.join(self.paths.get_rep_dir(), source.link)


    # configwa
    def load_config(self):
        encoding = Decoder.get_encoding(self.paths.get_config_file())
        local_data: dict[str, Any] = {}
        try:
            with open(self.paths.get_config_file(), encoding=encoding) as f:
                lines = f.readlines()
                lines = remove_git_merge_tags(lines)
                local_data = yaml.safe_load("\n".join(lines))
            if local_data is None or not isinstance(local_data, dict) or len(local_data) == 0: # type: ignore
                with open(self.paths.get_config_backup_file(), "r", encoding=encoding) as f:
                    lines = f.readlines()
                    lines = remove_git_merge_tags(lines)
                    local_data = yaml.safe_load("\n".join(lines))
            if local_data is None or not isinstance(local_data, dict) or len(local_data) == 0: # type: ignore
                raise FileNotFoundError(f"Arquivo de configuração vazio: {self.paths.get_config_file()}")
        except:
            raise Warning(Text.format("O arquivo de configuração do repositório {y} está {r}.\nAbra e corrija o conteúdo ou crie um novo.", self.paths.get_config_file(), "corrompido"))
        if local_data["version"] == "0.0.1":
            local_data["sources"] = [
                RepSource(database=Legacy.LEGACY_DATABASE, link=local_data["remote"], filters=local_data.get("filter", None)).save_to_dict(),
                self.get_default_local_source().save_to_dict()
            ]
        self.data.load_from_dict(local_data)

        for source in self.data.get_sources():
            source.set_local_info(self.paths.get_rep_dir(), self.paths.get_cache_folder())

        return self

    def get_default_local_source(self) -> RepSource:
        source = RepSource(database=RepSource.LOCAL_SOURCE_DATABASE, link="", filters=None)
        source.set_local_info(self.paths.get_rep_dir(), self.paths.get_cache_folder())
        return source

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