from pathlib import Path
from tko.config.run_settings import RunSettings

class RepositoryPaths:
    CFG_FILE = "repository.yaml"
    OLD_HISTORY_FILE = "history.csv"
    TASK_LOG_FILE = "task_log.csv"
    TRACK_FOLDER = "track"
    AUDIT_FOLDER = "audit"
    LOG_FOLDER = "log"
    CONFIG_FOLDER = ".tko"

    def __init__(self, repo_dir: Path | str, run_settings: RunSettings):
        self.root_dir: Path = Path(repo_dir) if isinstance(repo_dir, str) else repo_dir
        self.run_settings = run_settings

    @staticmethod
    def __walk_to_root(start: Path):
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
            for cfg in folder.rglob(f"{RepositoryPaths.CONFIG_FOLDER}/{RepositoryPaths.CFG_FILE}")
        ]
        return repos

    @staticmethod
    def rec_search_for_repo_parents(folder: Path) -> Path | None:
        for path in RepositoryPaths.__walk_to_root(folder):
            target: Path = path / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.CFG_FILE
            if target.is_file():
                return path
        return None
    
    @property
    def track_folder(self) -> Path:
        return self.root_dir / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.TRACK_FOLDER

    @property
    def log_folder(self) -> Path:
        return self.root_dir / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.LOG_FOLDER

    @property
    def audit_folder(self) -> Path:
        return self.root_dir / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.AUDIT_FOLDER

        
    @property
    def config_folder(self) -> Path:
        return self.root_dir / RepositoryPaths.CONFIG_FOLDER

    @property
    def config_file(self) -> Path:
        return self.root_dir / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.CFG_FILE
    
    @property
    def config_backup_file(self) -> Path:
        return Path(str(self.config_file) + ".backup")

    @property
    def old_history_file(self) -> Path:
        return self.root_dir / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.OLD_HISTORY_FILE

    def get_track_task_folder(self, label: str) -> Path:
        return self.root_dir / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.TRACK_FOLDER / label

    def get_audit_task_folder(self, label: str) -> Path:
        return self.root_dir / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.AUDIT_FOLDER / label