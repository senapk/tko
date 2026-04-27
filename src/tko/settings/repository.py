from __future__ import annotations
from pathlib import Path
from tko.settings.rep_data import RepData
from tko.settings.rep_data import RepData
from tko.settings.rep_source import RepSource
from tko.game.game import Game
from tko.logger.logger import Logger
import yaml # type: ignore
from tko.settings.rep_paths import RepPaths
from icecream import ic # type: ignore
from datetime import timedelta
from tko.settings.git_cache import GitCache
from tko.play.flags import Flags
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

    def set_global_cache(self):
        RepPaths.use_global_cache_folder = True
        update_mode = self.git_cache.update_mode
        self.git_cache = GitCache(self.paths.get_cache_folder(), timedelta(seconds=self.cache_time_for_remote_source), update_mode=update_mode)
        return self

    def found(self):
        return self.paths.get_config_file().exists()

    def is_inside_repo(self, path: Path) -> bool:
        rep_dir = self.paths.get_repo_root_dir()
        path = path.resolve()
        return path.is_relative_to(rep_dir)


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
    
    def get_task_folder_for_label(self, label: str) -> Path:
        parts: list[str] = label.split("@")
        source = ""
        if len(parts) > 1:
            source = parts[0]
            label = parts[1]
        return self.paths.root_dir / source / label


    def create_default_sandbox_source(self) -> RepSource:
        source = RepSource("", git_cache=self.git_cache).set_default_student_sandbox()
        source.set_source_globals(self.paths.get_repo_root_dir(), self.paths.get_cache_folder())
        return source


    def __str__(self) -> str:
        return f"data: {self.data}\n"
