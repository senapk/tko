from datetime import datetime
from pathlib import Path

from tko.logger.versions_writer import VersionsWriter
from tko.repository.task_migration import TaskDataMigration


def test_migration_combines_track_and_audit_into_history(tmp_path: Path) -> None:
    tko: Path = tmp_path / ".tko"
    tko.mkdir()
    (tko / "repository.toml").write_text(
        '[profile]\nauthoring_source = "course"\n'
        '[profile.sources.course]\nuri = "README.md"\n', encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("- [ ] [Task](labs/task/README.md)\n", encoding="utf-8")
    activity: Path = tmp_path / "labs/task"
    activity.mkdir(parents=True)
    (activity / "README.md").write_text("# Task\n", encoding="utf-8")

    for family, content in (("track", "execution"), ("audit", "audit")):
        path: Path = tko / family / "course@labs/task" / "solver.py.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        VersionsWriter().write(path, content, datetime(2026, 9, 15, 10 if family == "track" else 9, 0, 0))

    plan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert ".tko/history/course/labs/task/solver.py.jsonl" in {change.relative for change in plan.changes}
    assert ".tko/history/course/labs/task/events.jsonl" in {change.relative for change in plan.changes}
    assert plan.apply() is not None
    assert (tko / "history/course/labs/task/solver.py.jsonl").is_file()
    events: str = (tko / "history/course/labs/task/events.jsonl").read_text(encoding="utf-8")
    assert '"type":"audit"' in events
    assert not any(path.is_file() for path in (tko / "track").rglob("*") if (tko / "track").exists())
    assert not any(path.is_file() for path in (tko / "audit").rglob("*") if (tko / "audit").exists())
