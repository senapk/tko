from __future__ import annotations
from tko.logger.file_monitor import FileMonitor
from tko.repository.repository import Repository

class RepositoryWatcher:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.monitor: FileMonitor | None = None

    def start_watching(self) -> RepositoryWatcher:
        if self.monitor is not None:
            return self
            
        self.monitor = FileMonitor(
            root_directory=self.repo.root_dir,
            sources_dir_list={source.path.work_dir: source.data.name for source in self.repo.remotes},
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
