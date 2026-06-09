from datetime import datetime, timedelta
from pathlib import Path

from tko.logger.file_monitor import FileMonitor
from tko.logger.log_item_move import LogItemMove, LogItemMoveMode


class _FakeLogger:
    def __init__(self):
        self.items: list[LogItemMove] = []

    def store(self, item: LogItemMove) -> None:
        self.items.append(item)


class _TestFileMonitor(FileMonitor):
    def force_flush(self) -> None:
        self._save_events()

    def set_last_update(self, value: datetime) -> None:
        self._last_update = value


def test_file_monitor_flushes_logs_and_callback_grouped_by_task(tmp_path: Path) -> None:
    source_dir = tmp_path / "disc"
    task_dir = source_dir / "task01"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("task\n", encoding="utf-8")
    solver = task_dir / "solver.py"
    solver.write_text("print('x')\n", encoding="utf-8")

    logger = _FakeLogger()
    callback_payload: dict[str, list[Path]] = {}

    def on_flush(task_files: dict[str, list[Path]], _flushed_at: datetime) -> None:
        callback_payload.update(task_files)

    monitor = _TestFileMonitor(
        root_directory=tmp_path,
        sources_dir_list={source_dir: "disc"},
        ignore_patterns=[],
        second_interval=1,
        logger=logger,  # type: ignore[arg-type]
        on_flush_events=on_flush,
    )

    monitor.history[solver] = datetime.now() - timedelta(seconds=2)
    monitor.set_last_update(datetime.now() - timedelta(seconds=2))
    monitor.force_flush()

    assert len(logger.items) == 1
    assert logger.items[0].mode == LogItemMoveMode.EDIT
    assert logger.items[0].key == "disc@task01"
    assert callback_payload == {"disc@task01": [solver]}


def test_file_monitor_ignores_paths_outside_tasks(tmp_path: Path) -> None:
    source_dir = tmp_path / "disc"
    source_dir.mkdir(parents=True)
    file_outside_task = source_dir / "notes.txt"
    file_outside_task.write_text("notes\n", encoding="utf-8")

    logger = _FakeLogger()
    callback_called = {"value": False}

    def on_flush(task_files: dict[str, list[Path]], _flushed_at: datetime) -> None:
        _ = task_files
        callback_called["value"] = True

    monitor = _TestFileMonitor(
        root_directory=tmp_path,
        sources_dir_list={source_dir: "disc"},
        ignore_patterns=[],
        second_interval=1,
        logger=logger,  # type: ignore[arg-type]
        on_flush_events=on_flush,
    )

    monitor.history[file_outside_task] = datetime.now() - timedelta(seconds=2)
    monitor.set_last_update(datetime.now() - timedelta(seconds=2))
    monitor.force_flush()

    assert logger.items == []
    assert callback_called["value"] is False
