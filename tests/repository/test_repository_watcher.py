from datetime import datetime
from pathlib import Path
from collections.abc import Callable
from typing import Any, cast

from _pytest.monkeypatch import MonkeyPatch
import tko.repository.repository_watcher as watcher_module
from tko.repository.repository_watcher import RepositoryWatcher
from tko.repository.repository import Repository
from tko.repository.remote import Source
from tko.config.run_settings import RunSettings
from tko.game.task import Task
from tko.game.task_location import TaskLocation
from tko.game.task_enums import EvalMode


class _FakeMonitor:
    def __init__(self, **kwargs: Any):
        self.kwargs = kwargs
        self.started = False
        self.stopped = False
        self.observers: list[dict[str, Any]] = []

    def add_observer(self, interval_seconds: int, on_flush_events: Any) -> None:
        self.observers.append(
            {
                "interval_seconds": interval_seconds,
                "on_flush_events": on_flush_events,
            }
        )

    def init(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True


class _FakeAuditTracker:
    def __init__(self, _repo: Any, verbose: bool = False, interval_seconds: int = 5, versions_writer: Any | None = None):
        self.verbose = verbose
        self.interval_seconds = interval_seconds
        self.versions_writer = versions_writer
        self.calls: list[tuple[str, list[tuple[Path, datetime | None]]]] = []
        self.notification_callback: Callable[[str], None] | None = None

    def set_notification_callback(self, callback: Callable[[str], None] | None) -> None:
        self.notification_callback = callback

    def store(self, task_key: str, file_ts_list: list[tuple[Path, datetime | None]]) -> tuple[bool, int]:
        self.calls.append((task_key, file_ts_list))
        return True, 1


def _make_repo(tmp_path: Path) -> Repository:
    repo: Repository = Repository(tmp_path, RunSettings(), None, recursive_search=False)
    index: Path = tmp_path / "disc/README.md"
    repo.data.set_source(Source.from_local_file("disc", index))
    task: Task = Task()
    task.basic.source_name = "disc"
    task.basic.key = "task01"
    task.location = TaskLocation(index_path=index, raw_link="task01/README.md", eval=EvalMode.DIFF)
    repo.game.tasks[task.basic.full_key] = task
    return repo


def test_start_watching_uses_default_interval_when_audit_disabled(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    holder: dict[str, _FakeMonitor] = {}

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        monitor = _FakeMonitor(**kwargs)
        holder["monitor"] = monitor
        return monitor

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)

    repo = _make_repo(tmp_path)
    watcher = RepositoryWatcher(repo)
    watcher.start_watching(log_audit=False)

    monitor = holder["monitor"]
    assert monitor.started is True
    assert len(monitor.observers) == 1
    assert monitor.observers[0]["interval_seconds"] == 300
    assert callable(monitor.observers[0]["on_flush_events"])


def test_start_watching_enables_audit_callback_and_interval(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    holder: dict[str, _FakeMonitor] = {}

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        monitor = _FakeMonitor(**kwargs)
        holder["monitor"] = monitor
        return monitor

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)
    monkeypatch.setattr(watcher_module, "AuditTracker", _FakeAuditTracker)

    repo = _make_repo(tmp_path)
    task_dir = tmp_path / "disc" / "task01"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("task\n", encoding="utf-8")
    changed_file = task_dir / "solver.py"
    changed_file.write_text("print('x')\n", encoding="utf-8")

    watcher = RepositoryWatcher(repo)
    watcher.start_watching(log_audit=True, audit_interval_seconds=42)

    monitor = holder["monitor"]
    assert len(monitor.observers) == 2

    audit_entry = [o for o in monitor.observers if o["interval_seconds"] == 42][0]
    callback = audit_entry["on_flush_events"]
    assert callable(callback)

    ts = datetime.now()
    callback({changed_file: ts})

    assert watcher.audit_tracker is not None
    fake_tracker = cast(_FakeAuditTracker, watcher.audit_tracker)
    assert fake_tracker.verbose is False
    assert fake_tracker.interval_seconds == 42
    assert fake_tracker.calls == [("disc@task01", [(changed_file, ts)])]


def test_start_watching_audit_verbose_is_forwarded(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    holder: dict[str, _FakeMonitor] = {}

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        monitor = _FakeMonitor(**kwargs)
        holder["monitor"] = monitor
        return monitor

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)
    monkeypatch.setattr(watcher_module, "AuditTracker", _FakeAuditTracker)

    repo = _make_repo(tmp_path)
    watcher = RepositoryWatcher(repo)
    watcher.start_watching(log_audit=True, audit_verbose=True)

    assert watcher.audit_tracker is not None
    fake_tracker = cast(_FakeAuditTracker, watcher.audit_tracker)
    assert fake_tracker.verbose is True
    assert fake_tracker.interval_seconds == watcher.default_audit_interval_seconds


def test_watcher_forwards_audit_notifications(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        return _FakeMonitor(**kwargs)

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)
    monkeypatch.setattr(watcher_module, "AuditTracker", _FakeAuditTracker)
    watcher = RepositoryWatcher(_make_repo(tmp_path))
    watcher.start_watching(log_audit=True)
    messages: list[str] = []

    watcher.set_audit_notification_callback(messages.append)

    assert watcher.audit_tracker is not None
    tracker = cast(_FakeAuditTracker, watcher.audit_tracker)
    assert tracker.notification_callback is not None
    tracker.notification_callback("[audit] 10:11:12 disc@task01")
    assert messages == ["[audit] 10:11:12 disc@task01"]


def test_start_watching_is_idempotent_when_already_running(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    calls = {"ctor": 0}

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        calls["ctor"] += 1
        return _FakeMonitor(**kwargs)

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)

    repo = _make_repo(tmp_path)
    watcher = RepositoryWatcher(repo)
    watcher.start_watching()
    watcher.start_watching()

    assert calls["ctor"] == 1


def test_audit_is_owned_by_one_watcher_per_workspace(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monitors: list[_FakeMonitor] = []

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        monitor = _FakeMonitor(**kwargs)
        monitors.append(monitor)
        return monitor

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)
    monkeypatch.setattr(watcher_module, "AuditTracker", _FakeAuditTracker)
    repo = _make_repo(tmp_path)

    first = RepositoryWatcher(repo)
    second = RepositoryWatcher(repo)
    first.start_watching(log_audit=True)
    second.start_watching(log_audit=True)

    assert first.audit_lock_acquired is True
    assert second.audit_lock_acquired is False
    assert first.audit_tracker is not None
    assert second.audit_tracker is None

    first.stop_watching()
    second.stop_watching()
    second.start_watching(log_audit=True)
    assert second.audit_lock_acquired is True
    second.stop_watching()


def test_stop_watching_resets_state(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    holder: dict[str, _FakeMonitor] = {}

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        monitor = _FakeMonitor(**kwargs)
        holder["monitor"] = monitor
        return monitor

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)
    monkeypatch.setattr(watcher_module, "AuditTracker", _FakeAuditTracker)

    repo = _make_repo(tmp_path)
    watcher = RepositoryWatcher(repo)
    watcher.start_watching(log_audit=True)
    watcher.stop_watching()

    assert holder["monitor"].stopped is True
    assert watcher.monitor is None
    assert watcher.edit_logger is None
    assert watcher.audit_logger is None


def test_start_watching_defaults_to_persistent_audit_flag(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    holder: dict[str, _FakeMonitor] = {}

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        monitor = _FakeMonitor(**kwargs)
        holder["monitor"] = monitor
        return monitor

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)
    monkeypatch.setattr(watcher_module, "AuditTracker", _FakeAuditTracker)

    repo = _make_repo(tmp_path)
    watcher = RepositoryWatcher(repo)
    watcher.start_watching()

    monitor = holder["monitor"]
    assert len(monitor.observers) == 1
