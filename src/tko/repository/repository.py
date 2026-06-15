from __future__ import annotations
from pathlib import Path
from tko.config.run_settings import RunSettings
from tko.config.user_data import UserData
from tko.repository.repository_data import RepositoryData
from tko.repository.remote import Remote
from tko.game.game import Game
from tko.logger.logger import Logger
from tko.repository.repository_paths import RepositoryPaths
from icecream import ic # type: ignore
from tko.repository.git_cache import GitCache
from tko.config.flags import Flags
from tko.game.task import Task

class Repository:
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

    def __init__(self, folder: Path, rs: RunSettings, git_cache: GitCache | None, recursive_search: bool = True) -> None:
        if git_cache is None:
            self.git_cache = GitCache(cache_dir=UserData.global_cache_dir(), update_mode=rs.update_mode)
        else:
            self.git_cache = git_cache
        rep_folder: Path = folder
        if recursive_search:
            recursive_folder = RepositoryPaths.rec_search_for_repo_parents(folder)
            if recursive_folder is not None:
                rep_folder = recursive_folder
        self.paths = RepositoryPaths(rep_folder, rs)
        self.data: RepositoryData = RepositoryData()
        self.game = Game()
        self.flags = Flags()
        self.logger: Logger = Logger(rep_folder, rs)

    def found(self):
        return self.paths.config_file.exists()

    @property
    def audit(self):
        return self.data.audit

    @property
    def audit_enabled(self) -> bool:
        return self.data.audit.enabled

    @audit_enabled.setter
    def audit_enabled(self, value: bool) -> None:
        self.data.audit.enabled = value

    @property
    def audit_interval_seconds(self) -> int | None:
        return self.data.audit.interval_seconds

    @audit_interval_seconds.setter
    def audit_interval_seconds(self, value: int | None) -> None:
        self.data.audit.interval_seconds = value

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
            if t.resource.is_read:
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
