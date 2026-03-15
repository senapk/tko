import os
from pathlib import Path
from platformdirs import user_cache_dir

class RepPaths:
    CFG_FILE = "repository.yaml"
    OLD_HISTORY_FILE = "history.csv"
    TASK_LOG_FILE = "task_log.csv"
    DAILY_FILE = "daily.yaml"
    TRACK_FOLDER = "track"
    LOG_FOLDER = "log"
    CACHE_FOLDER = "cache"
    CONFIG_FOLDER = ".tko"
    use_global_cache_folder: bool =  False # teacher tools, to avoid rewrite cache in student repos

    def __init__(self, repo_dir: Path | str):
        self.root_folder: Path = Path(repo_dir) if isinstance(repo_dir, str) else repo_dir

    @staticmethod
    def walk_to_root(start: Path):
        current: Path = start.resolve()
        while True:
            yield current
            if current.parent == current:
                break
            current = current.parent

    @staticmethod
    def rec_search_for_repo_subdir(folder: Path) -> list[Path]:
        repos: list[Path] = [
            cfg.parent.parent
            for cfg in folder.rglob(f"{RepPaths.CONFIG_FOLDER}/{RepPaths.CFG_FILE}")
        ]
        return repos

    @staticmethod
    def rec_search_for_repo_parents(folder: Path) -> Path | None:
        for path in RepPaths.walk_to_root(folder):
            target: Path = path / RepPaths.CONFIG_FOLDER / RepPaths.CFG_FILE
            if target.is_file():
                return path

        return None
    
    def get_track_folder(self) -> Path:
        return self.root_folder / RepPaths.CONFIG_FOLDER / RepPaths.TRACK_FOLDER

    def get_log_folder(self) -> Path:
        return self.root_folder / RepPaths.CONFIG_FOLDER / RepPaths.LOG_FOLDER

    def get_cache_folder(self) -> Path:
        if RepPaths.use_global_cache_folder:
            return Path(user_cache_dir("tko")) / RepPaths.CACHE_FOLDER
        return self.root_folder / RepPaths.CONFIG_FOLDER / RepPaths.CACHE_FOLDER

    def get_track_task_folder(self, label: str) -> Path:
        return self.root_folder / RepPaths.CONFIG_FOLDER / RepPaths.TRACK_FOLDER / label

    def get_config_folder(self) -> Path:
        return self.root_folder / RepPaths.CONFIG_FOLDER

    def get_config_file(self) -> Path:
        return self.root_folder / RepPaths.CONFIG_FOLDER / RepPaths.CFG_FILE

    def get_config_backup_file(self) -> Path:
        return Path(str(self.get_config_file()) + ".backup")

    def get_old_history_file(self) -> Path:
        return self.root_folder / RepPaths.CONFIG_FOLDER / RepPaths.OLD_HISTORY_FILE

    def get_workspace_dir(self) -> Path:
        return self.root_folder

    def has_local_config_file(self) -> bool:
        return os.path.exists(self.get_config_file())