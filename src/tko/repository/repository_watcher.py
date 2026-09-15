from __future__ import annotations
from collections.abc import Callable

from tko.logger.file_monitor import FileMonitor
from tko.logger.audit_tracker import AuditTracker
from tko.repository.audit_logger import AuditLogger
from tko.repository.edit_logger import EditLogger
from tko.repository.repository import Repository
from loguru import logger
from tko.logger.versions_writer import VersionsWriter
from tko.repository.audit_coordinator import AuditAlreadyRunning, AuditCoordinator


class RepositoryWatcher:
    default_edit_interval_seconds = 300
    default_audit_interval_seconds = 20

    def __init__(self, repo: Repository):
        self.repo = repo
        self.monitor: FileMonitor | None = None
        self.edit_logger: EditLogger | None = None
        self.audit_logger: AuditLogger | None = None
        self.audit_tracker: AuditTracker | None = None
        self.versions_writer: VersionsWriter = VersionsWriter()
        self.audit_coordinator = AuditCoordinator(repo.root_dir)
        self.audit_lock_acquired: bool = False

    def set_audit_notification_callback(self, callback: Callable[[str], None] | None) -> None:
        if self.audit_tracker is not None:
            self.audit_tracker.set_notification_callback(callback)

    def start_watching(
        self,
        log_edits: bool = True,
        log_audit: bool = False,
        audit_verbose: bool = False,
        audit_interval_seconds: int | None = None,
        strict_audit: bool = False,
    ) -> RepositoryWatcher:
        if self.monitor is not None:
            return self
        
        self.monitor = FileMonitor(root_directory=self.repo.root_dir)
        
        if log_edits:
            logger.debug("Starting edit logger with interval of {} seconds".format(self.default_edit_interval_seconds))
            second_interval = self.default_edit_interval_seconds
            self.edit_logger = EditLogger(task_lookup=self.repo, logger=self.repo.logger)
            self.monitor.add_observer(interval_seconds=second_interval, on_flush_events=self.edit_logger.on_flush_events)
        
        if log_audit:
            try:
                self.audit_coordinator.acquire()
                self.audit_lock_acquired = True
            except AuditAlreadyRunning:
                if strict_audit:
                    raise
                logger.info(self.audit_coordinator.description())
                log_audit = False

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
            self.audit_logger = AuditLogger(task_lookup=self.repo, audit_tracker=self.audit_tracker)
            self.monitor.add_observer(interval_seconds=audit_interval_seconds, on_flush_events=self.audit_logger.on_flush_events)

        try:
            self.monitor.init()
        except Exception:
            self.audit_coordinator.release()
            self.audit_lock_acquired = False
            self.monitor = None
            raise
        return self
    
    def stop_watching(self) -> RepositoryWatcher:
        if self.monitor is not None:
            self.monitor.stop()
            self.monitor = None
        self.audit_coordinator.release()
        self.audit_lock_acquired = False
        self.edit_logger = None
        self.audit_logger = None
        self.audit_tracker = None
        return self
