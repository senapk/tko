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

    def init(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True


class _FakeAuditTracker:
    def __init__(self, _repo: Any):
        self.calls: list[tuple[str, list[Path]]] = []

    def store(self, task_key: str, files: list[Path]) -> tuple[bool, int]:
        self.calls.append((task_key, files))
        return True, 0


def _make_repo(tmp_path: Path, enabled: bool, interval: int) -> Any:
    def _store(_item: Any) -> None:
        return None

    remote = SimpleNamespace(
        path=SimpleNamespace(work_dir=tmp_path / "disc"),
        data=SimpleNamespace(name="disc"),
    )
    return SimpleNamespace(
        root_dir=tmp_path,
        remotes=[remote],
        ignore_patterns=[],
        logger=SimpleNamespace(store=_store),
        data=SimpleNamespace(audit=SimpleNamespace(enabled=enabled, interval_seconds=interval)),
    )


def test_start_watching_uses_default_interval_when_audit_disabled(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    holder: dict[str, _FakeMonitor] = {}

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        monitor = _FakeMonitor(**kwargs)
        holder["monitor"] = monitor
        return monitor

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)

    repo = _make_repo(tmp_path, enabled=False, interval=77)
    watcher = RepositoryWatcher(repo)
    watcher.start_watching()

    assert holder["monitor"].started is True
    assert holder["monitor"].kwargs["second_interval"] == 300
    assert holder["monitor"].kwargs["on_flush_events"] is None


def test_start_watching_enables_audit_callback_and_interval(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    holder: dict[str, _FakeMonitor] = {}

    def fake_monitor_ctor(**kwargs: Any) -> _FakeMonitor:
        monitor = _FakeMonitor(**kwargs)
        holder["monitor"] = monitor
        return monitor

    monkeypatch.setattr(watcher_module, "FileMonitor", fake_monitor_ctor)
    monkeypatch.setattr(watcher_module, "AuditTracker", _FakeAuditTracker)

    repo = _make_repo(tmp_path, enabled=True, interval=42)
    watcher = RepositoryWatcher(repo)
    watcher.start_watching()

    callback = holder["monitor"].kwargs["on_flush_events"]
    assert callable(callback)
    assert holder["monitor"].kwargs["second_interval"] == 42

    changed_file = tmp_path / "disc" / "task01" / "solver.py"
    callback({"disc@task01": [changed_file]}, None)

    assert watcher.audit_tracker is not None
    fake_tracker = cast(_FakeAuditTracker, watcher.audit_tracker)
    assert fake_tracker.calls == [("disc@task01", [changed_file])]

    watcher.stop_watching()
    assert holder["monitor"].stopped is True
    assert watcher.monitor is None
    assert watcher.audit_tracker is None
