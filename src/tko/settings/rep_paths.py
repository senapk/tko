import os

class RepPaths:
    CFG_FILE = "repository.yaml"
    OLD_HISTORY_FILE = "history.csv"
    TASK_LOG_FILE = "task_log.csv"
    DAILY_FILE = "daily.yaml"
    INDEX_FILE = "Readme.md"
    TRACK_FOLDER = "track"
    LOG_FOLDER = "log"
    CONFIG_FOLDER = ".tko"

    def __init__(self, rep_dir: str):
        self.root_folder = rep_dir

    @staticmethod
    def rec_search_for_repo(folder: str) -> str:
        abs_folder: str = os.path.abspath(folder)
        if os.path.exists(os.path.join(abs_folder, RepPaths.CONFIG_FOLDER, RepPaths.CFG_FILE)):
            return abs_folder
        new_folder = os.path.dirname(abs_folder)
        if new_folder == abs_folder: # não encontrou, não tem mais como subir
            return ""
        return RepPaths.rec_search_for_repo(new_folder)
    
    def get_track_folder(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, RepPaths.CONFIG_FOLDER, RepPaths.TRACK_FOLDER))

    def get_log_folder(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, RepPaths.CONFIG_FOLDER, RepPaths.LOG_FOLDER))

    def get_track_task_folder(self, label: str) -> str:
        return os.path.abspath(os.path.join(self.root_folder, RepPaths.CONFIG_FOLDER, RepPaths.TRACK_FOLDER, label))

    def get_config_folder(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, RepPaths.CONFIG_FOLDER))

    def get_config_file(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, RepPaths.CONFIG_FOLDER, RepPaths.CFG_FILE))

    def get_config_backup_file(self) -> str:
        return self.get_config_file() + ".backup"
    
    def get_old_history_file(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, RepPaths.CONFIG_FOLDER, RepPaths.OLD_HISTORY_FILE))

    def get_default_readme_path(self) -> str:
        return os.path.abspath(os.path.join(self.root_folder, RepPaths.INDEX_FILE))

    def get_rep_dir(self) -> str:
        return os.path.abspath(self.root_folder)
    
    def has_local_config_file(self) -> bool:
        return os.path.exists(self.get_config_file())