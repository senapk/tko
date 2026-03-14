from __future__ import annotations
from pathlib import Path
from tko.settings.rep_data import RepData
from typing import Any
from tko.settings.rep_data import RepData
from tko.settings.rep_source import RepSource
from tko.game.game import Game
from tko.util.decoder import Decoder
from tko.util.text import Text
from tko.logger.logger import Logger
import yaml # type: ignore
from tko.settings.rep_paths import RepPaths
from icecream import ic # type: ignore
from datetime import timedelta
from tko.settings.git_cache import GitCache
import os

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

    def __init__(self, folder: Path, force_update: bool = False):
        rep_folder: Path = folder
        recursive_folder = RepPaths.rec_search_for_repo(folder)
        if recursive_folder is not None:
            rep_folder = recursive_folder
        self.paths = RepPaths(rep_folder)
        self.data: RepData = RepData()
        self.game = Game()
        self.logger: Logger = Logger(rep_folder) 
        self.force_update: bool = force_update
        self.cache = GitCache(self.paths.get_cache_folder(), timedelta(seconds=self.cache_time_for_remote_source))

    def found(self):
        return self.paths.get_config_file().exists()

    def is_local_dir(self, path: Path) -> bool:
        rep_dir = self.paths.get_workspace_dir()
        path = path.resolve()
        return path.is_relative_to(rep_dir)

    def load_game(self, try_update: bool = True, silent: bool = False) -> Repository:
        if not self.data.get_sources():
            self.load_config()
        if try_update:
            for source in self.data.get_sources():
                _ = source.get_source_readme() # to ensure cache path is set
        sources: list[RepSource] = self.data.get_sources()
        self.game.set_sources(sources, self.data.lang, silent=silent)
        self.__load_tasks_from_rep_into_game()
        return self
    
    def get_key_from_task_folder(self, folder: Path) -> str:
        path = folder.resolve()
        parts = path.parts
        label = parts[-1]
        workspace = parts[-2]
        return f"{workspace}@{label}"

    def is_task_folder(self, folder: Path) -> bool:
        label = folder.name
        task_folder = self.get_task_folder_for_label(label)
        return task_folder == folder
    
    def __load_tasks_from_rep_into_game(self):
        # load tasks from repository.yaml into game
        tasks = self.data.tasks
        for key, serial in tasks.items():
            if key in self.game.tasks:
                self.game.tasks[key].load_from_db(serial)

    def get_task_folder_for_label(self, label: str) -> Path:
        parts: list[str] = label.split("@")
        source = ""
        if len(parts) > 1:
            source = parts[0]
            label = parts[1]
        return self.paths.root_folder / source / label


    def load_config(self):
        content = Decoder.load(self.paths.get_config_file())
        local_data: dict[str, Any] = {}
        try:
            lines = content.splitlines()
            lines = remove_git_merge_tags(lines)
            local_data = yaml.safe_load("\n".join(lines))
            if local_data is None or not isinstance(local_data, dict) or len(local_data) == 0: # type: ignore
                backup_content = Decoder.load(self.paths.get_config_backup_file())
                lines = backup_content.splitlines()
                lines = remove_git_merge_tags(lines)
                local_data = yaml.safe_load("\n".join(lines))
            if local_data is None or not isinstance(local_data, dict) or len(local_data) == 0: # type: ignore
                raise FileNotFoundError(f"Arquivo de configuração vazio: {self.paths.get_config_file()}")
        except:
            raise Warning(Text.format("O arquivo de configuração do repositório {y} está {r}.\nAbra e corrija o conteúdo ou crie um novo.", self.paths.get_config_file(), "corrompido"))
        self.data.load_from_dict(local_data)
        self.data.ensure_sandbox_source(self.paths.get_workspace_dir())

        for source in self.data.get_sources():
            source.set_rep_globals(self.paths.get_workspace_dir(), self.paths.get_cache_folder())

        return self

    def get_student_sandbox(self) -> RepSource:
        source = RepSource("").set_student_sandbox()
        source.set_rep_globals(self.paths.get_workspace_dir(), self.paths.get_cache_folder())
        return source


    def save_config(self):
        self.data.version = "0.2"

        path: Path = Path(self.paths.get_config_file())
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_yaml(path, self.data.save_to_dict())
        return self

    def __str__(self) -> str:
        return f"data: {self.data}\n"
        

def atomic_write_yaml(path: Path, data: dict[str, Any]) -> None:
    tmp: Path = path.with_suffix(path.suffix + ".tmp")

    with tmp.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

        f.flush()
        os.fsync(f.fileno())

    tmp.replace(path)

    # fsync do diretório (POSIX apenas)
    if os.name == "posix":
        dir_fd: int = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)