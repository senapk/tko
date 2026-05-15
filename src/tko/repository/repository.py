from __future__ import annotations
from pathlib import Path
from tko.repository.repository_data import RepositoryData
from tko.repository.repository_data import RepositoryData
from tko.repository.remote import Remote
from tko.game.game import Game
from tko.logger.logger import Logger
from tko.repository.repository_paths import RepositoryPaths
from icecream import ic # type: ignore
from datetime import timedelta
from tko.repository.git_cache import GitCache, UpdateMode
from tko.config.flags import Flags
from tko.game.task import Task

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

    def __init__(self, folder: Path, update_mode: UpdateMode = UpdateMode.IF_OLDER, recursive_search: bool = True):
        rep_folder: Path = folder
        if recursive_search:
            recursive_folder = RepositoryPaths.rec_search_for_repo_parents(folder)
            if recursive_folder is not None:
                rep_folder = recursive_folder
        self.paths = RepositoryPaths(rep_folder)
        self.git_cache = GitCache(cache_dir=self.paths.cache_folder, max_age=timedelta(seconds=self.cache_time_for_remote_source), update_mode=update_mode)
        self.data: RepositoryData = RepositoryData()
        self.game = Game()
        self.flags = Flags()
        self.logger: Logger = Logger(rep_folder)

    def set_global_cache(self):
        RepositoryPaths.use_global_cache_folder = True
        update_mode = self.git_cache.update_mode
        self.git_cache = GitCache(self.paths.cache_folder, timedelta(seconds=self.cache_time_for_remote_source), update_mode=update_mode)
        return self

    def found(self):
        return self.paths.config_file.exists()

    @property
    def remotes(self) -> list[Remote]:
        remotes: list[Remote] = []
        for remote in self.data.remotes_raw_list:
            remote.git_cache = self.git_cache
            remote.root_dir = self.root_dir
            remotes.append(remote)
        return remotes

    @property
    def root_dir(self) -> Path:
        return self.paths.root_dir

    def get_task_from_task_folder(self, folder: Path) -> Task | None:
        folder = folder.resolve()
        for t in self.game.tasks.values():
            if t.resource.is_view:
                continue
            work_dir = t.path.work_dir
            if work_dir is None:
                continue
            if folder.is_relative_to(work_dir):
                return t
        return None

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

    def create_default_sandbox_source(self) -> Remote:
        source = Remote("")
        source.is_sandbox = True
        return source


    def __str__(self) -> str:
        return f"data: {self.data}\n"
