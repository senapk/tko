from tko.logger.log_item_move import LogItemMove, LogItemMoveMode
from tko.logger.logger import Logger
from tko.util.find_source_key_task_key import find_source_key_task_key


from datetime import datetime
from pathlib import Path


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