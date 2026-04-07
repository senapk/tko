from pathlib import Path
import threading
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEvent
from tko.logger.logger import Logger
from tko.logger.log_item_move import LogItemMove


class _EventManipulator(PatternMatchingEventHandler):
    def __init__(
        self,
        history_records: dict[Path, datetime],
        ignore_patterns: list[str],
    ) -> None:
        super().__init__(
            patterns=["*"],
            ignore_patterns=ignore_patterns,
            ignore_directories=True,
            case_sensitive=False
        )
        self.historico: dict[Path, datetime] = history_records

    def on_created(self, event: FileSystemEvent) -> None:
        pass

    def on_modified(self, event: FileSystemEvent) -> None:
        self.historico[Path(str(event.src_path))] = datetime.now()

    def on_deleted(self, event: FileSystemEvent) -> None:
        pass


class FileMonitor:
    def __init__(
        self,
        root_directory: Path,
        sources_dir_list: dict[Path, str],
        ignore_patterns: list[str] | None, 
        second_interval: int, 
        logger: Logger
    ) -> None:
        self.root_directory: Path = root_directory
        self.sources_dir_list: dict[Path, str] = {s.resolve(): source_name for s, source_name in sources_dir_list.items()}
        self.history: dict[Path, datetime] = {}
        self.ignore_patterns: list[str] = ignore_patterns or []
        self.seconds_interval: int = second_interval
        self.logger: Logger = logger
        self._last_update: datetime = datetime.now()
        self._observer = Observer()
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()
        self._running: bool = False

    def find_source_key_task_key(self, path: Path) -> str | None:
        for source_dir, source_name in self.sources_dir_list.items():
            try:
                relative_path = path.resolve().relative_to(source_dir.resolve())
                first_parent = relative_path.parts[0] if relative_path.parts else ""
                if not (source_dir/first_parent/"README.md").exists():
                    return None
                return f"{source_name}@{first_parent}"
            except ValueError:
                continue
        return None

    def _save_events(self) -> None:
            now = datetime.now()
            if (now - self._last_update).total_seconds() < self.seconds_interval:
                return
            self._last_update = now
            for path, stamp in self.history.items():
                full_key = self.find_source_key_task_key(path)
                if full_key is None:
                    continue
                self.logger.store(
                    LogItemMove()
                    .set_datetime(stamp)
                    .set_mode(LogItemMove.Mode.EDIT)
                    .set_key(full_key)
                )
            self.history.clear()
            

    def _init_observer(self) -> None:
        handler = _EventManipulator(
            self.history,
            ignore_patterns=self.ignore_patterns
        )

        self._observer.schedule(handler, str(self.root_directory), recursive=True)
        self._observer.start()

        try:
            while not self._stop_event.is_set():
                self._save_events()
                time.sleep(0.5)
        finally:
            self._observer.stop()
            self._observer.join()

    def init(self) -> None:
        if self._running:
            return

        self._running = True
        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._init_observer,
            args=(),
            daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        if not self._running:
            return

        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self._running = False
