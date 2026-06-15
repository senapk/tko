from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from _pytest.monkeypatch import MonkeyPatch
import tko.repository.repository_watcher as watcher_module
from tko.repository.repository_watcher import RepositoryWatcher


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
    def __init__(self, _repo: Any, verbose: bool = False, interval_seconds: int = 5):
        self.verbose = verbose
        self.interval_seconds = interval_seconds
        self.calls: list[tuple[str, list[tuple[Path, datetime | None]]]] = []

    def store(self, task_key: str, file_ts_list: list[tuple[Path, datetime | None]]) -> tuple[bool, int]:
        self.calls.append((task_key, file_ts_list))
        return True, 1


def _make_repo(tmp_path: Path) -> Any:
    def _store(_item: Any) -> None:
        return None

    remote_root = tmp_path / "disc"
    remote = SimpleNamespace(
        path=SimpleNamespace(work_dir=remote_root),
        data=SimpleNamespace(name="disc"),
    )
    return SimpleNamespace(
        root_dir=tmp_path,
        remotes=[remote],
        ignore_patterns=[],
        paths=SimpleNamespace(config_folder=tmp_path / ".tko"),
        logger=SimpleNamespace(store=_store),
        audit=SimpleNamespace(enabled=False, interval_seconds=None),
        data=SimpleNamespace(audit_enabled=False, audit_interval_seconds=None),
    )


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
    repo.audit.enabled = True
    watcher = RepositoryWatcher(repo)
    watcher.start_watching()

    monitor = holder["monitor"]
    assert len(monitor.observers) == 2
