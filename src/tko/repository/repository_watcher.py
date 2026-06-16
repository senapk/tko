from __future__ import annotations
from pathlib import Path
from tko.logger.file_monitor import FileMonitor
from tko.logger.audit_tracker import AuditTracker
from tko.repository.audit_logger import AuditLogger
from tko.repository.edit_logger import EditLogger
from tko.repository.repository import Repository
from loguru import logger
from tko.logger.versions_writer import VersionsWriter


class RepositoryWatcher:
    default_edit_interval_seconds = 300
    default_audit_interval_seconds = 20

    def __init__(self, repo: Repository):
        self.repo = repo
        self.monitor: FileMonitor | None = None
        self.edit_logger: EditLogger | None = None
        self.audit_logger: AuditLogger | None = None
        self.versions_writer: VersionsWriter = VersionsWriter()

    def start_watching(
        self,
        log_edits: bool = True,
        log_audit: bool = False,
        audit_verbose: bool = False,
        audit_interval_seconds: int | None = None,
    ) -> RepositoryWatcher:
        if self.monitor is not None:
            return self
        
        sources_dir_list: dict[Path, str] = {source.path.work_dir: source.data.name for source in self.repo.remotes}
        self.monitor = FileMonitor(root_directory=self.repo.root_dir)
        
        if log_edits:
            logger.debug("Starting edit logger with interval of {} seconds".format(self.default_edit_interval_seconds))
            second_interval = self.default_edit_interval_seconds
            self.edit_logger = EditLogger(sources_dir_list=sources_dir_list, logger=self.repo.logger)
            self.monitor.add_observer(interval_seconds=second_interval, on_flush_events=self.edit_logger.on_flush_events)
        
        if log_audit:
            if audit_interval_seconds is None:
                audit_interval_seconds = self.default_audit_interval_seconds
            logger.debug("Starting audit logger with interval of {} seconds".format(audit_interval_seconds))
            self.audit_tracker = AuditTracker(
                self.repo,
                verbose=audit_verbose,
                interval_seconds=audit_interval_seconds,
                versions_writer=self.versions_writer,
            )
            self.audit_logger = AuditLogger(source_dir_list=sources_dir_list, audit_tracker=self.audit_tracker)
            self.monitor.add_observer(interval_seconds=audit_interval_seconds, on_flush_events=self.audit_logger.on_flush_events)

        self.monitor.init()
        return self
    
    def stop_watching(self) -> RepositoryWatcher:
        if self.monitor is not None:
            self.monitor.stop()
            self.monitor = None
        self.edit_logger = None
        self.audit_logger = None
        return self
