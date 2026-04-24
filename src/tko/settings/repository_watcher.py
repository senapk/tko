from tko.logger.file_monitor import FileMonitor
from tko.settings.repository import Repository

class RepositoryWatcher:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.monitor: FileMonitor | None = None

    def start_watching(self) -> 'RepositoryWatcher':
        if self.monitor is not None:
            return self
            
        self.monitor = FileMonitor(
            root_directory=self.repo.paths.get_repo_root_dir(),
            sources_dir_list={source.get_workspace(): source.name for source in self.repo.data.get_sources()},
            ignore_patterns=self.repo.ignore_patterns,
            second_interval=300,
            logger=self.repo.logger
        )
        self.monitor.init()
        return self
    
    def stop_watching(self) -> 'RepositoryWatcher':
        if self.monitor is not None:
            self.monitor.stop()
            self.monitor = None
        return self
