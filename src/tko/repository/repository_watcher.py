from __future__ import annotations
from pathlib import Path
from typing import Callable
from tko.logger.file_monitor import FileMonitor
from tko.logger.audit_tracker import AuditTracker
from tko.repository.repository import Repository

class RepositoryWatcher:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.monitor: FileMonitor | None = None
        self.audit_tracker: AuditTracker | None = None

    def start_watching(self) -> RepositoryWatcher:
        if self.monitor is not None:
            return self

        audit_enabled = self.repo.data.audit.enabled
        second_interval = self.repo.data.audit.interval_seconds if audit_enabled else 300

        flush_callback: Callable[[dict[str, list[Path]], object], None] | None = None
        if audit_enabled:
            self.audit_tracker = AuditTracker(self.repo)

            def _on_flush_events(task_files: dict[str, list[Path]], _: object) -> None:
                if self.audit_tracker is None:
                    return
                for task_key, files in task_files.items():
                    self.audit_tracker.store(task_key=task_key, files=files)
            flush_callback = _on_flush_events
            
        self.monitor = FileMonitor(
            root_directory=self.repo.root_dir,
            sources_dir_list={source.path.work_dir: source.data.name for source in self.repo.remotes},
            ignore_patterns=self.repo.ignore_patterns,
            second_interval=second_interval,
            logger=self.repo.logger,
            on_flush_events=flush_callback,
        )
        self.monitor.init()
        return self
    
    def stop_watching(self) -> RepositoryWatcher:
        if self.monitor is not None:
            self.monitor.stop()
            self.monitor = None
        self.audit_tracker = None
        return self
