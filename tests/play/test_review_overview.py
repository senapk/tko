"""Class comparison uses the same task key for every student."""

from __future__ import annotations

import csv
from pathlib import Path

from tko.config.run_settings import RunSettings
from tko.play.review_overview import ReviewOverviewService, ReviewTaskRow


def _student(parent: Path, name: str, *, with_task: bool = True) -> Path:
    folder: Path = parent / name
    config: Path = folder / ".tko"
    config.mkdir(parents=True)
    (config / "repository.toml").write_text(
        'version = "0.3"\n[profile]\nauthoring_source = "course"\n'
        '[profile.sources.course]\nuri = "README.md"\n', encoding="utf-8",
    )
    if with_task:
        activity: Path = folder / "plan/task"
        activity.mkdir(parents=True)
        (activity / "README.md").write_text("# Task\n", encoding="utf-8")
        (folder / "README.md").write_text(
            "# Course\n## Plan\n- [ ] `@plan/task eval=self` [Task](plan/task/README.md)\n",
            encoding="utf-8",
        )
    else:
        (folder / "README.md").write_text("# Course\n", encoding="utf-8")
    return folder


def test_overview_collects_all_students_and_exports_csv(tmp_path: Path) -> None:
    first: Path = _student(tmp_path, "alice")
    second: Path = _student(tmp_path, "bob", with_task=False)
    log: Path = first / ".tko/log"
    log.mkdir()
    (log / "2026-09-14.log").write_text(
        "2026-09-14 10:00:00, EXEC, v:1, k:course@plan/task\n"
        "2026-09-14 10:01:00, SELF, v:1, k:course@plan/task, rate:80, self:1\n",
        encoding="utf-8",
    )
    service: ReviewOverviewService = ReviewOverviewService(
        [first, second], RunSettings(changedir=tmp_path),
    )
    key: str = "course@plan/task"

    alice: ReviewTaskRow = service.row(key, 0)
    bob: ReviewTaskRow = service.row(key, 1)

    assert alice.status == "ok"
    assert alice.grade == 80
    assert alice.executions == 1
    assert alice.feedback is True
    assert alice.last_event is not None
    assert bob.status == "tarefa ausente"
    assert bob.grade is None

    output: Path = tmp_path / "turma.csv"
    service.export_csv(output, key, [alice, bob])
    with output.open(encoding="utf-8", newline="") as stream:
        rows: list[dict[str, str]] = list(csv.DictReader(stream))
    assert len(rows) == 2
    assert rows[0]["student"] == "alice"
    assert rows[0]["grade"] == "80.0"
    assert rows[1]["status"] == "tarefa ausente"
    assert rows[1]["grade"] == ""


def test_overview_migrates_legacy_student_and_keeps_error_row(tmp_path: Path) -> None:
    old: Path = _student(tmp_path, "alice")
    (old / ".tko/repository.toml").write_text(
        'version = "0.2"\nsandbox_name = "course"\nsandbox_index = "README.md"\n',
        encoding="utf-8",
    )
    pending: Path = _student(tmp_path, "bob")
    (pending / ".tko/migration-pending.json").write_text("{}\n", encoding="utf-8")
    service: ReviewOverviewService = ReviewOverviewService(
        [old, pending], RunSettings(changedir=tmp_path),
    )

    assert service.row("course@plan/task", 0).status == "sem atividade"
    assert (old / ".tko/task-format.json").exists()
    failed: ReviewTaskRow = service.row("course@plan/task", 1)
    assert failed.status == "erro"
    assert "recover" in failed.error
    assert (pending / ".tko/migration-pending.json").exists()


def test_overview_cache_can_invalidate_one_student(tmp_path: Path) -> None:
    folder: Path = _student(tmp_path, "alice")
    service: ReviewOverviewService = ReviewOverviewService([folder], RunSettings(changedir=tmp_path))
    first: ReviewTaskRow = service.row("course@plan/task", 0)
    (folder / "README.md").write_text("# Course\n", encoding="utf-8")

    assert service.row("course@plan/task", 0) is first
    service.invalidate(0)
    assert service.row("course@plan/task", 0).status == "tarefa ausente"
