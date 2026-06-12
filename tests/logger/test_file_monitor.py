from datetime import datetime, timedelta
from pathlib import Path

from tko.logger.file_monitor import FileMonitor


class _TestFileMonitor(FileMonitor):
    def force_flush(self) -> None:
        self._save_events()


def test_file_monitor_flushes_observer_callback_with_changed_files(tmp_path: Path) -> None:
    task_dir = tmp_path / "disc" / "task01"
    task_dir.mkdir(parents=True)
    solver = task_dir / "solver.py"
    solver.write_text("print('x')\n", encoding="utf-8")

    callback_payload: dict[Path, datetime] = {}

    def on_flush(changed_files: dict[Path, datetime]) -> None:
        callback_payload.update(changed_files)

    monitor = _TestFileMonitor(root_directory=tmp_path)
    monitor.add_observer(interval_seconds=1, on_flush_events=on_flush)

    obs = monitor.file_action_observers[0]
    ts = datetime.now() - timedelta(seconds=2)
    obs.change_log[solver] = ts
    obs.last_update = datetime.now() - timedelta(seconds=2)

    monitor.force_flush()

    assert callback_payload == {solver: ts}
    assert obs.change_log == {}


def test_file_monitor_callback_is_not_called_when_no_changes(tmp_path: Path) -> None:
    callback_called = {"value": False}

    def on_flush(_changed_files: dict[Path, datetime]) -> None:
        callback_called["value"] = True

    monitor = _TestFileMonitor(root_directory=tmp_path)
    monitor.add_observer(interval_seconds=1, on_flush_events=on_flush)

    obs = monitor.file_action_observers[0]
    obs.last_update = datetime.now() - timedelta(seconds=2)

    monitor.force_flush()

    assert callback_called["value"] is False
