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
from datetime import datetime
from tko.util.runner import Runner



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

    def down_source_from_remote_url(self, source: RepSource) -> bool:
        cache_file = source.get_file_path()
        os.makedirs(self.paths.get_cache_folder(), exist_ok=True)
        #print("debug", source.get_url_link(), cache_file)
        ru = RemoteUrl(source.get_url_link())
        try:
            ru.download_absolute_to(cache_file)
            return True
        except urllib.error.URLError: # type: ignore
            print(f"Não foi possível baixar o arquivo do repositório alias:{source.database}, link:{source.get_url_link()}")
            if os.path.exists(cache_file):
                print("Usando arquivo do cache")
            else:
                raise Warning("fail: Arquivo do cache não encontrado")
        return False

    def run_git_cmd(self, cmd_list: list[str], folder: str)-> bool:
        error, stdout, stderr = Runner.subprocess_run(cmd_list, folder=folder, timeout=60)
        if error != 0:
            print(f"Não foi possível atualizar o repositório clonado em {folder}. Erro: {stdout}\n{stderr}")
            return False
        return True

    def git_pull_repository(self, source: RepSource) -> bool:
        basedir = source.get_git_folder()
        branch_name = source.branch if source.branch is not None else "master"
        print("Verificando atualizações do repositório clonado em", basedir)
        if not self.run_git_cmd(["git", "fetch", "--all"], basedir):
            return False
        if not self.run_git_cmd(["git", "reset", "--hard", f"origin/{branch_name}"], folder=basedir):
            return False
        if not self.run_git_cmd(["git", "clean", "-df"], folder=basedir):
            return False
        return True


    def is_in_cache(self, source: RepSource, now_dt: datetime) -> bool:
        last_dt = Delta.decode_format(source.cache_timestamp)
        if os.path.isfile(source.get_file_path()) == False:
            return False
        if (now_dt - last_dt).total_seconds() < Repository.cache_time_for_remote_source:
            time_missing = Repository.cache_time_for_remote_source - (now_dt - last_dt).total_seconds()
            r = int(time_missing / 60)
            print(f"Usando cache do repositório {source.database} ({source.get_url_link()}), próxima atualização em {r} minutos")
            return True
        return False

    def clone_repository_git(self, link: str, target: str) -> bool:
        os.makedirs(target, exist_ok=True)
        result = self.run_git_cmd(["git", "clone", "--depth", "1", link, target], folder=".")
        if not result:
            print(Text.format("fail: Não foi possível clonar o repositório {y}.\nErro: {r}", link))
            return False
        return True

    def update_cache_path(self, source: RepSource) -> None:
        if source.source_type == RepSource.Type.FILE:
            return

        if source.source_type == RepSource.Type.LINK:
            now_str, now_dt = Delta.now()
            # verify if cache file exists and is less than 1 hour old
            if not self.force_update and os.path.isfile(source.get_file_path()) and source.cache_timestamp != "":
                if self.is_in_cache(source, now_dt):
                    return
            if self.down_source_from_remote_url(source):
                source.cache_timestamp = now_str
            return
        
        if source.source_type == RepSource.Type.CLONE:
            now_str, now_dt = Delta.now()
            if not self.force_update and source.cache_timestamp != "" and os.path.exists(source.get_file_path()):
                if self.is_in_cache(source, now_dt):
                    return

            if not os.path.exists(source.get_file_path()) and self.clone_repository_git(source.get_url_link(), source.get_git_folder()):
                source.cache_timestamp = now_str
            elif self.git_pull_repository(source):
                source.cache_timestamp = now_str
            return

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
                RepSource(database=Legacy.LEGACY_DATABASE, link=local_data["remote"], source_type=RepSource.Type.LINK, filters=local_data.get("filter", None)).save_to_dict(),
                self.get_default_local_source().save_to_dict()
            ]
        self.data.load_from_dict(local_data)

        for source in self.data.get_sources():
            source.set_local_info(self.paths.get_rep_dir(), self.paths.get_cache_folder())

        return self

    def get_default_local_source(self) -> RepSource:
        source = RepSource(database=RepSource.LOCAL_SOURCE_DATABASE, link="", source_type=RepSource.Type.FILE, filters=None)
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