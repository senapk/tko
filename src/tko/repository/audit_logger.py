from tko.logger.audit_tracker import AuditTracker
from tko.util.find_source_key_task_key import find_source_key_task_key
from datetime import datetime
from pathlib import Path

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