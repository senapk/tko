from pathlib import Path
import threading
import time
from datetime import datetime
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEvent
from loguru import logger

# create type alias for the flush callback
FlushCallbackType = Callable[[dict[Path, datetime]], None]

class FileActionObserver:
    def __init__( self, interval_seconds: int, on_flush_events: FlushCallbackType ) -> None:
        self.interval_seconds: int = interval_seconds
        self.change_log: dict[Path, datetime] = {}
        self.on_flush_events: FlushCallbackType = on_flush_events
        self.last_update: datetime = datetime.now()

class _EventManipulator(PatternMatchingEventHandler):
    def __init__( self, file_action_observers: list[FileActionObserver], ignore_patterns: list[str]) -> None:
        super().__init__(
            patterns=["*"],
            ignore_patterns=ignore_patterns,
            ignore_directories=True,
            case_sensitive=False
        )
        self.file_action_observers: list[FileActionObserver] = file_action_observers

    def on_created(self, event: FileSystemEvent) -> None:
        pass

    def on_modified(self, event: FileSystemEvent) -> None:
        for observer in self.file_action_observers:
            observer.change_log[Path(str(event.src_path))] = datetime.now()

    def on_deleted(self, event: FileSystemEvent) -> None:
        pass


class FileMonitor:
    ignore_patterns = [
        "*.tmp", "*.log", "*.bak", "*.swp", "*~", "watcher.lock", 
        "*.last", "*.auditlog", "*.editlog", "*.json", "*.jsonl", 
        "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.pdf", "*.docx", 
        "*.xlsx", "*.pptx", "Readme.md", "extra.md", 
        "*.tio", ".vpl"]

    def __init__(
        self,
        root_directory: Path,
    ) -> None:
        self._observer = Observer()
        self.file_action_observers: list[FileActionObserver] = []
        self.root_directory: Path = root_directory
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()
        self._running: bool = False

    def add_observer(self, interval_seconds: int, on_flush_events: FlushCallbackType) -> None:
        observer = FileActionObserver(
            interval_seconds=interval_seconds,
            on_flush_events=on_flush_events
        )
        self.file_action_observers.append(observer)

    def _check_save_events(self) -> None:
            now = datetime.now()
            for file_observer in self.file_action_observers:
                if (now - file_observer.last_update).total_seconds() >= file_observer.interval_seconds:
                    file_observer.last_update = now
                    if file_observer.on_flush_events is None:
                        continue
                    if not file_observer.change_log:
                        continue
                    try:
                        data = file_observer.change_log
                        file_observer.change_log = {}
                        file_observer.on_flush_events(data)
                    except Exception as e:
                        logger.warning(f"Failed to flush events: {e}")

    def _init_observer(self) -> None:
        handler = _EventManipulator(self.file_action_observers, ignore_patterns=self.ignore_patterns)
        self._observer.schedule(handler, str(self.root_directory), recursive=True)
        self._observer.start()

        try:
            while not self._stop_event.is_set():
                self._check_save_events()
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
