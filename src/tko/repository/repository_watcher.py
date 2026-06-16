from __future__ import annotations
from pathlib import Path
from tko.logger.file_monitor import FileMonitor
from tko.logger.audit_tracker import AuditTracker
from tko.repository.repository import Repository
from tko.logger.logger import Logger
from tko.logger.log_item_move import LogItemMove, LogItemMoveMode
from datetime import datetime
from loguru import logger
from tko.logger.versions_writer import VersionsWriter



def find_source_key_task_key(sources_dir_map: dict[Path, str], path: Path) -> str | None:
    for source_dir, source_name in sources_dir_map.items():
        try:
            relative_path = path.resolve().relative_to(source_dir.resolve())
            first_parent = relative_path.parts[0] if relative_path.parts else ""
            if not (source_dir/first_parent/"README.md").exists():
                return None
            return f"{source_name}@{first_parent}"
        except ValueError:
            continue
    return None

class EditLogger:
    def __init__(self, sources_dir_list: dict[Path, str], logger: Logger) -> None:
        self.sources_dir_list: dict[Path, str] = {s.resolve(): source_name for s, source_name in sources_dir_list.items()}
        self.logger: Logger = logger
        
    def on_flush_events(self, changed_files: dict[Path, datetime]) -> None:
        for path, timestamp in changed_files.items():
            full_key = find_source_key_task_key(self.sources_dir_list, path)
            if full_key is None:
                continue
            self.logger.store(
                LogItemMove()
                .set_datetime(timestamp)
                .set_mode(LogItemMoveMode.EDIT)
                .set_key(full_key)
            )

class AuditLogger:
    def __init__(self, source_dir_list: dict[Path, str], audit_tracker: AuditTracker) -> None:
        self.sources_dir_list = source_dir_list
        self.audit_tracker = audit_tracker

    def on_flush_events(self, changed_files: dict[Path, datetime]) -> None:
        task_files_map: dict[str, list[tuple[Path, datetime|None]]] = {}
        for path, timestamp in changed_files.items():
            full_key = find_source_key_task_key(self.sources_dir_list, path)
            if not full_key:
                continue
            if not full_key in task_files_map:
                task_files_map[full_key] = []
            task_files_map[full_key].append((path, timestamp))

        for task_key, file_ts_list in task_files_map.items():
            self.audit_tracker.store(task_key=task_key, file_ts_list=file_ts_list)


class RepositoryWatcher:
    default_edit_interval_seconds = 300
    default_audit_interval_seconds = 15

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
