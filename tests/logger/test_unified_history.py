from pathlib import Path

from tko.logger.history import HistoryEvent, append_event
from tko.logger.tracker import Tracker


def test_execution_tracker_writes_snapshots_and_unified_event(tmp_path: Path) -> None:
    task: Path = tmp_path / "history" / "course" / "labs" / "task"
    source: Path = tmp_path / "solver.py"
    source.write_text("print(1)\n", encoding="utf-8")

    tracker: Tracker = Tracker().set_folder(task / "files")
    tracker.set_event_folder(task).set_task_root(tmp_path).set_files([source]).set_result("100%")
    changed: tuple[bool, int] = tracker.store()

    assert changed[0] is True
    assert (task / "files" / "solver.py.jsonl").is_file()
    event: str = (task / "events.jsonl").read_text(encoding="utf-8")
    assert '"type":"execution"' in event
    assert '"result":"100%"' in event


def test_history_events_are_append_safe(tmp_path: Path) -> None:
    path: Path = tmp_path / "events.jsonl"
    append_event(path, HistoryEvent("2026-09-15_10-00-00", "audit", ("solver.py",)))
    append_event(path, HistoryEvent("2026-09-15_10-01-00", "execution", ("solver.py",), "50%"))

    lines: list[str] = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert '"type":"audit"' in lines[0]
    assert '"type":"execution"' in lines[1]


def test_duplicate_events_are_not_appended(tmp_path: Path) -> None:
    path: Path = tmp_path / "events.jsonl"
    event = HistoryEvent("2026-09-15_10-00-00", "audit", ("solver.py",))
    append_event(path, event)
    append_event(path, event)

    assert path.read_text(encoding="utf-8").count("solver.py") == 1
