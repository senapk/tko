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
from tko.play.flags import Flags
from tko.logger.log_sort import LogSort
from tko.logger.file_monitor import FileMonitor
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

    ignore_patterns = [
        "*.log",
        ".git/*",
        "*/.git*",
        "*/.vscode/*",
        "*/.idea/*",
        "*/__pycache__/*",
        "*/.pytest_cache/*",
        "*/.venv/*",
    ]

    def __init__(self, folder: Path, update_mode: GitCache.UpdateMode = GitCache.UpdateMode.IF_OLDER, recursive_search: bool = True):
        rep_folder: Path = folder
        if recursive_search:
            recursive_folder = RepPaths.rec_search_for_repo_parents(folder)
            if recursive_folder is not None:
                rep_folder = recursive_folder
        self.paths = RepPaths(rep_folder)
        self.git_cache = GitCache(cache_dir=self.paths.get_cache_folder(), max_age=timedelta(seconds=self.cache_time_for_remote_source), update_mode=update_mode)
        self.data: RepData = RepData(self.git_cache)
        self.game = Game()
        self.flags = Flags()
        self.logger: Logger = Logger(rep_folder)
        self.watcher: FileMonitor | None = None

    def set_global_cache(self):
        RepPaths.use_global_cache_folder = True
        update_mode = self.git_cache.update_mode
        self.git_cache = GitCache(self.paths.get_cache_folder(), timedelta(seconds=self.cache_time_for_remote_source), update_mode=update_mode)
        return self

    def found(self):
        return self.paths.get_config_file().exists()

    def is_inside_repo(self, path: Path) -> bool:
        rep_dir = self.paths.get_workspace_dir()
        path = path.resolve()
        return path.is_relative_to(rep_dir)

    def load_game(self, silent: bool = False) -> Repository:
        if not self.data.get_sources():
            self.load_config()
        if self.git_cache.update_mode == GitCache.UpdateMode.ALWAYS:
            for source in self.data.get_sources():
                _ = source.get_source_readme() # to ensure cache path is set
        sources: list[RepSource] = self.data.get_sources()
        self.game.set_sources(sources, self.data.lang, silent=silent).build()
        self.__load_tasks_from_log_into_game()
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
    
    def __load_tasks_from_log_into_game(self):
        task_dict: dict[str, LogSort] = self.logger.tasks.task_dict
        for key, task_log in task_dict.items():
            if not key in self.game.tasks:
                continue
            task = self.game.tasks[key]
            self_list = task_log.self_list
            if self_list:
                _, self_item = self_list[-1]
                task.info.copy_quality_from(self_item.info)

            exec_list = task_log.exec_list
            if exec_list:
                _, exec_item = exec_list[-1]
                task.info.rate = exec_item.rate


    def get_task_folder_for_label(self, label: str) -> Path:
        parts: list[str] = label.split("@")
        source = ""
        if len(parts) > 1:
            source = parts[0]
            label = parts[1]
        return self.paths.root_dir / source / label

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
        self.flags.from_dict(self.data.get_flags())
        for source in self.data.get_sources():
            source.set_source_globals(self.paths.get_workspace_dir(), self.paths.get_cache_folder())

        return self

    def start_watching(self):
        if self.watcher is not None:
            return self
        self.watcher = FileMonitor(
            root_directory=self.paths.get_workspace_dir(),
            sources_dir_list={source.get_workspace(): source.name for source in self.data.get_sources()},
            ignore_patterns=self.ignore_patterns,
            second_interval=300,
            logger=self.logger
        )
        self.watcher.init()
        return self
    
    def stop_watching(self):
        if self.watcher is not None:
            self.watcher.stop()
            self.watcher = None
        return self

    def get_student_sandbox(self) -> RepSource:
        source = RepSource("", git_cache=self.git_cache).set_student_sandbox()
        source.set_source_globals(self.paths.get_workspace_dir(), self.paths.get_cache_folder())
        return source


    def save_config(self):
        self.data.version = "0.2"
        self.data.flags = self.flags.to_dict()
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