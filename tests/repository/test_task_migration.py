from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import tomllib

import pytest
from typer.testing import CliRunner

from tko.cli.cli_tools import app
from tko.config.run_settings import RunSettings
from tko.game.game import Game
from tko.logger.log_history import LogHistory
from tko.logger.log_item_base import LogItemBase
from tko.logger.tracker import Track, Tracker
from tko.logger.task_listener import TaskListener
from tko.repository.repository import Repository
from tko.repository.task_data_format import (
    FORMAT_BYTES, FORMAT_FILE, PENDING_FILE, MigrationRequiredError,
    initialize_task_data, require_current_task_data,
)
from tko.repository.task_migration import TaskDataMigration, read_mapping
from tko.repository.task_migration_transaction import MigrationPlan, recover_migration
import tko.repository.task_migration_transaction as transaction


def _write(root: Path, relative: str, content: str | bytes) -> Path:
    path: Path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_bytes(content.encode() if isinstance(content, str) else content)
    return path


def _workspace(root: Path, index: str | None = None) -> Path:
    _write(root, ".tko/repository.toml", 'version = "0.3"\n[profile]\nauthoring_source = "course"\n[profile.sources.course]\nuri = "README.md"\n')
    return _write(root, "README.md", index if index is not None else "# Course\n## Basics\n- [ ] `@old eval=diff` [Task](plan/task/README.md)\n")


def _event(key: str, minute: int, kind: str = "EXEC", fields: str = "") -> str:
    return f"2026-09-14 10:{minute:02d}:00, {kind}, v:1, k:{key}{fields}\n"


def _snapshot(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def _listener(lines: str) -> TaskListener:
    listener: TaskListener = TaskListener()
    entries: dict[str, LogItemBase] = {}
    for line in lines.splitlines():
        item: LogItemBase | None = LogHistory.decode_line(line)
        assert item is not None
        entries[str(item)] = item
    for item in sorted(entries.values(), key=lambda event: event.datetime):
        listener.handle_log_entry(item)
    return listener


def test_preview_is_read_only_and_apply_preserves_mixed_history(tmp_path: Path) -> None:
    index: Path = _workspace(tmp_path)
    config: Path = tmp_path / ".tko/repository.toml"
    config.write_text(config.read_text() + '[state]\nselected = "course@old"\npinned = ["course@old"]\nexpanded = ["course@basics"]\n[extension]\nvalue = 2.5\n')
    # Out-of-order events, all supported kinds and a duplicated canonical event.
    lines: str = _event("course@plan/task", 4) + _event("course@old", 0, "MOVE", ", mode:PICK") + _event("course@old", 2, "SELF", ", rate:50") + _event("course@plan/task", 4)
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", lines)
    legacy: Path = _write(tmp_path, ".tko/track/course@old/src/main.py.jsonl", b'{"history":"untouched"}\n')
    _write(tmp_path, ".tko/audit/course/old/src/main.py.jsonl", b"snapshot bytes\n")
    solution: Path = _write(tmp_path, "course/old/src/main.py", b"print(42)\n")
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert plan.mapping["course@old"] == "course@plan/task"
    assert _snapshot(tmp_path) == before
    with pytest.raises(MigrationRequiredError, match="tko tool migrate"):
        Repository(tmp_path, RunSettings(), None, recursive_search=False)

    backup: Path | None = plan.apply()
    assert backup is not None
    assert (backup / "before/.tko/log/2026-09-14.log").read_text() == lines
    assert not legacy.exists()
    assert (tmp_path / ".tko/track/course/plan/task/src/main.py.jsonl").read_bytes() == b'{"history":"untouched"}\n'
    assert (tmp_path / ".tko/audit/course/plan/task/src/main.py.jsonl").read_bytes() == b"snapshot bytes\n"
    assert not solution.exists()
    assert (tmp_path / "plan/task/src/main.py").read_bytes() == before[solution.relative_to(tmp_path).as_posix()]
    assert index.read_bytes() == before["README.md"]
    parsed: object = tomllib.loads(config.read_text())
    assert isinstance(parsed, dict)
    assert parsed["state"] == {"selected": "course@plan/task", "pinned": ["course@plan/task"], "expanded": ["course@basics"]}
    assert parsed["extension"] == {"value": 2.5}
    expected: str = lines.replace("k:course@old", "k:course@plan/task")
    assert log.read_text() == expected
    repo: Repository = Repository(tmp_path, RunSettings(), None, recursive_search=False)
    actual: TaskListener = repo.logger.tasks
    canonical: TaskListener = _listener(expected)
    assert len(repo.logger.history.get_entries()) == 3
    assert list(actual.task_dict) == ["course@plan/task"]
    assert actual.task_dict["course@plan/task"].base_list[-1][0].accumulated == dt.timedelta(minutes=4)
    assert actual.task_dict["course@plan/task"].base_list[-1][0].accumulated == canonical.task_dict["course@plan/task"].base_list[-1][0].accumulated
    assert len(actual.mount_task_history(Game(), {}, {"course@plan/task"})) == 1
    assert actual.mount_task_history(Game(), {}, {"course@old"}) == []
    after: dict[str, bytes] = _snapshot(tmp_path)
    assert TaskDataMigration(tmp_path).inspect().apply() is None
    assert _snapshot(tmp_path) == after


def test_preserves_unknown_log_fields_versions_and_crlf(tmp_path: Path) -> None:
    _workspace(tmp_path)
    original: bytes = _event("course@old", 0, fields=", custom:abc").replace("v:1", "v:9").replace("\n", "\r\n").encode()
    path: Path = _write(tmp_path, ".tko/log/2026-09-14.log", original)
    TaskDataMigration(tmp_path).inspect().apply()
    assert path.read_bytes() == original.replace(b"k:course@old", b"k:course@plan/task")


def test_ambiguous_alias_requires_explicit_map(tmp_path: Path) -> None:
    index: str = "- [ ] `@old` [A](plan/a/README.md)\n- [ ] `@old` [B](plan/b/README.md)\n"
    _workspace(tmp_path, index)
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@old", 0))
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    before: dict[str, bytes] = _snapshot(tmp_path)
    assert plan.errors
    with pytest.raises(ValueError):
        plan.apply()
    assert _snapshot(tmp_path) == before
    mapping: Path = _write(tmp_path, "map.json", '{"course@old": "course@plan/old"}')
    TaskDataMigration(tmp_path, read_mapping(mapping)).inspect().apply()
    assert "course@plan/old" in log.read_text()


def test_missing_alias_moves_activity_and_history_to_labs(tmp_path: Path) -> None:
    _workspace(tmp_path, "- [ ] [Task](plan/old/README.md)\n")
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@old", 0))
    history: Path = _write(tmp_path, ".tko/track/course@old/draft.py.json", b"snapshot")
    activity: Path = _write(tmp_path, "course/old/main.py", b"print(42)\n")

    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()

    assert plan.errors == []
    assert plan.mapping["course@old"] == "course@labs/old"
    plan.apply()
    assert "course@labs/old" in log.read_text()
    assert not history.exists()
    assert (tmp_path / ".tko/track/course/labs/old/draft.py.json").read_bytes() == b"snapshot"
    assert not activity.exists()
    assert (tmp_path / "course/labs/old/main.py").read_bytes() == b"print(42)\n"


def test_same_labels_in_two_sources_do_not_merge(tmp_path: Path) -> None:
    _workspace(tmp_path)
    config: Path = tmp_path / ".tko/repository.toml"
    config.write_text(config.read_text() + '[profile.sources.other]\nuri = "other.md"\n')
    _write(tmp_path, "other.md", "- [ ] `@old` [Other](nested/plan/task/README.md)\n")
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@old", 0) + _event("other@old", 2))
    TaskDataMigration(tmp_path).inspect().apply()
    assert set(_listener(log.read_text()).task_dict) == {"course@plan/task", "other@nested/plan/task"}


@pytest.mark.parametrize("same", [True, False])
def test_history_collisions_only_merge_identical_files(tmp_path: Path, same: bool) -> None:
    _workspace(tmp_path)
    _write(tmp_path, ".tko/track/course@old/main.jsonl", b"original")
    target: Path = _write(tmp_path, ".tko/track/course/plan/task/main.jsonl", b"original" if same else b"different")
    _write(tmp_path, ".tko/track/course/old/extra.jsonl", b"extra")
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    if same:
        assert plan.errors == []
        plan.apply()
        assert target.read_bytes() == b"original"
        assert (target.parent / "extra.jsonl").read_bytes() == b"extra"
    else:
        before: dict[str, bytes] = _snapshot(tmp_path)
        assert any("Conflicting" in error for error in plan.errors)
        with pytest.raises(ValueError):
            plan.apply()
        assert _snapshot(tmp_path) == before


def test_track_csv_migrates_to_jsonl_without_writing_during_dry_run(tmp_path: Path) -> None:
    _workspace(tmp_path)
    legacy: Path = _write(tmp_path, ".tko/track/course@old/track.csv", "2026-09-14_10-00-00,100%,main.py:2026-09-14_10-00-00\n")
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert _snapshot(tmp_path) == before
    destination: Path = tmp_path / ".tko/track/course/plan/task/track.jsonl"
    preview = CliRunner().invoke(app, ["migrate", str(tmp_path), "--dry-run"])
    assert preview.exit_code == 0
    assert "create: .tko/track/course/plan/task/track.jsonl" in preview.output
    assert "delete: .tko/track/course@old/track.csv" in preview.output
    assert _snapshot(tmp_path) == before
    assert any(change.relative == destination.relative_to(tmp_path).as_posix() and change.after is not None for change in plan.changes)
    assert any(change.relative == legacy.relative_to(tmp_path).as_posix() and change.after is None for change in plan.changes)
    plan.apply()
    assert not legacy.exists()
    assert [track.identity() for track in Tracker.load_from_log(str(destination))] == [
        ("2026-09-14_10-00-00", "100%", ("main.py:2026-09-14_10-00-00",))
    ]
    after: dict[str, bytes] = _snapshot(tmp_path)
    assert TaskDataMigration(tmp_path).inspect().apply() is None
    assert _snapshot(tmp_path) == after


def test_track_histories_merge_sort_and_remove_only_exact_duplicates(tmp_path: Path) -> None:
    _workspace(tmp_path)
    old: Path = _write(tmp_path, ".tko/track/course@old/track.csv", "2026-09-14_10-02-00,80%,main.py:2026-09-14_10-02-00\n2026-09-14_10-00-00,50%,\n2026-09-14_10-00-00,50%,\n")
    canonical_csv: Path = _write(tmp_path, ".tko/track/course/plan/task/track.csv", "2026-09-14_10-01-00,70%,\n2026-09-14_10-02-00,90%,\n")
    canonical_jsonl: Path = _write(tmp_path, ".tko/track/course/plan/task/track.jsonl", Track().set_timestamp("2026-09-14_09-59-00").set_result("10%").to_json_line())
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert not any("Conflicting histories" in error for error in plan.errors)
    plan.apply()
    assert not old.exists()
    assert not canonical_csv.exists()
    records: list[Track] = Tracker.load_from_log(str(canonical_jsonl))
    assert [(item.timestamp, item.result) for item in records[:3]] == [
        ("2026-09-14_09-59-00", "10%"),
        ("2026-09-14_10-00-00", "50%"),
        ("2026-09-14_10-01-00", "70%"),
    ]
    assert {(item.timestamp, item.result) for item in records[3:]} == {
        ("2026-09-14_10-02-00", "80%"),
        ("2026-09-14_10-02-00", "90%"),
    }
    assert next(item for item in records if item.result == "80%").file_stamp_list == ["main.py:2026-09-14_10-02-00"]


@pytest.mark.parametrize(("filename", "content"), [
    ("track.csv", "2026-09-14_10-00-00,100%\n"),
    ("track.csv", "invalid,100%,\n"),
    ("track.jsonl", '{"timestamp":"invalid","result":"100%","files":[]}\n'),
    ("track.jsonl", '{"timestamp":"2026-09-14_10-00-00","result":"100%","files":[1]}\n'),
])
def test_invalid_track_record_blocks_all_migration_writes(tmp_path: Path, filename: str, content: str) -> None:
    _workspace(tmp_path)
    bad: Path = _write(tmp_path, f".tko/track/course@old/{filename}", content)
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert any(f"{bad}:1:" in error for error in plan.errors)
    with pytest.raises(ValueError):
        plan.apply()
    assert _snapshot(tmp_path) == before


def test_track_csv_merge_recovers_after_interrupted_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _workspace(tmp_path)
    _write(tmp_path, ".tko/track/course@old/track.csv", "2026-09-14_10-00-00,50%,\n")
    _write(tmp_path, ".tko/track/course/plan/task/track.csv", "2026-09-14_10-01-00,70%,\n")
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    original_write = transaction.atomic_bytes

    def interrupted_write(path: Path, content: bytes) -> None:
        if path == tmp_path / ".tko" / FORMAT_FILE:
            raise OSError("simulated interruption")
        original_write(path, content)

    with monkeypatch.context() as patch:
        patch.setattr(transaction, "atomic_bytes", interrupted_write)
        with pytest.raises(OSError, match="simulated interruption"):
            plan.apply()
    recover_migration(tmp_path)
    restored: dict[str, bytes] = {name: content for name, content in _snapshot(tmp_path).items() if not name.startswith(".tko/migrations/")}
    assert restored == before


@pytest.mark.parametrize("line", ["broken\n", _event("course@old", 0, "UNKNOWN"), _event("course@old", 0, fields=", k:course@old")])
def test_malformed_logs_block_all_writes(tmp_path: Path, line: str) -> None:
    _workspace(tmp_path)
    _write(tmp_path, ".tko/log/2026-09-14.log", line)
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors
    with pytest.raises(ValueError):
        plan.apply()
    assert _snapshot(tmp_path) == before


def test_yaml_state_and_old_csv_preserve_other_fields(tmp_path: Path) -> None:
    _write(tmp_path, ".tko/repository.yaml", "version: '0.2'\nsandbox_name: course\nsandbox_index: README.md\nselected: course@old\nflags:\n  show_time: 'true'\naudit:\n  interval_seconds: null\n")
    _write(tmp_path, "README.md", "- [ ] `@old` [Task](plan/task/README.md)\n")
    csv: Path = _write(tmp_path, ".tko/history.csv", 'hash,2026-09-14 10:00:00,SELF,course@old,"{c: 50, a: 1}"\n')
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert not plan.errors
    plan.apply()
    assert "course@plan/task" in csv.read_text()
    assert '"{c: 50, a: 1}"' in csv.read_text()
    assert not (tmp_path / ".tko/repository.yaml").exists()
    migrated: dict[str, object] = tomllib.loads((tmp_path / ".tko/repository.toml").read_text())
    assert migrated["state"] == {"selected": "course@plan/task"}
    profile: object = migrated["profile"]
    assert isinstance(profile, dict)
    assert profile["audit"] == {}
    assert migrated["preferences"] == {"show_time": "true"}


def test_legacy_toml_configuration_is_converted_before_loading(tmp_path: Path) -> None:
    _write(tmp_path, ".tko/repository.toml", 'version = "0.2"\nsandbox_name = "course"\nsandbox_index = "README.md"\nselected = "course@old"\n[flags]\nshow_time = "true"\n[extension]\nvalue = 7\n')
    _write(tmp_path, "README.md", "- [ ] `@old` [Task](plan/task/README.md)\n")
    before: dict[str, bytes] = _snapshot(tmp_path)
    with pytest.raises(MigrationRequiredError, match="Configuração antiga"):
        Repository(tmp_path, RunSettings(), None, recursive_search=False)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert _snapshot(tmp_path) == before
    backup: Path | None = plan.apply()
    assert backup is not None
    config: dict[str, object] = tomllib.loads((tmp_path / ".tko/repository.toml").read_text())
    assert "sandbox_name" not in config and "flags" not in config
    assert config["state"] == {"selected": "course@plan/task"}
    assert config["preferences"] == {"show_time": "true"}
    assert config["extension"] == {"value": 7}
    profile: object = config["profile"]
    assert isinstance(profile, dict)
    assert profile["authoring_source"] == "course"
    assert profile["sources"] == {"course": {"uri": "README.md"}}
    assert (backup / "before/.tko/repository.toml").read_bytes() == before[".tko/repository.toml"]
    assert TaskDataMigration(tmp_path).inspect().apply() is None


def test_yaml_without_task_history_still_requires_migration(tmp_path: Path) -> None:
    _write(tmp_path, ".tko/repository.yaml", "version: '0.2'\nsandbox_name: course\nsandbox_index: README.md\n")
    _write(tmp_path, "README.md", "# Course\n")
    with pytest.raises(MigrationRequiredError, match="Configuração antiga"):
        Repository(tmp_path, RunSettings(), None, recursive_search=False)
    TaskDataMigration(tmp_path).inspect().apply()
    assert not (tmp_path / ".tko/repository.yaml").exists()
    assert (tmp_path / ".tko/repository.toml").exists()
    Repository(tmp_path, RunSettings(), None, recursive_search=False)


def test_unknown_yaml_null_blocks_conversion_without_losing_data(tmp_path: Path) -> None:
    _write(tmp_path, ".tko/repository.yaml", "version: '0.2'\nsandbox_name: course\nsandbox_index: README.md\ncustom: null\n")
    _write(tmp_path, "README.md", "# Course\n")
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert any("TOML cannot represent null" in error for error in plan.errors)
    with pytest.raises(ValueError):
        plan.apply()
    assert _snapshot(tmp_path) == before


def test_recovery_after_interrupted_apply_restores_originals(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _workspace(tmp_path)
    _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@old", 0))
    _write(tmp_path, ".tko/track/course@old/main.jsonl", b"snapshot")
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    original_write = transaction.atomic_bytes

    def interrupted_write(path: Path, content: bytes) -> None:
        if path == tmp_path / ".tko" / FORMAT_FILE:
            raise OSError("simulated interruption")
        original_write(path, content)

    with monkeypatch.context() as patch:
        patch.setattr(transaction, "atomic_bytes", interrupted_write)
        with pytest.raises(OSError, match="simulated"):
            plan.apply()
    with pytest.raises(MigrationRequiredError, match="--recover"):
        require_current_task_data(tmp_path)
    backup: Path = recover_migration(tmp_path)
    assert backup.is_dir()
    assert not (tmp_path / ".tko" / PENDING_FILE).exists()
    restored: dict[str, bytes] = {name: content for name, content in _snapshot(tmp_path).items() if not name.startswith(".tko/migrations/")}
    assert restored == before
    TaskDataMigration(tmp_path).inspect().apply()
    require_current_task_data(tmp_path)


def test_changed_input_prevents_stale_plan_application(tmp_path: Path) -> None:
    index: Path = _workspace(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    index.write_text("changed")
    with pytest.raises(ValueError, match="changed"):
        plan.apply()
    assert not (tmp_path / ".tko/migrations").exists()


def test_new_workspace_marks_format_before_first_write(tmp_path: Path) -> None:
    repo: Repository = Repository(tmp_path, RunSettings(), None, recursive_search=False)
    item: LogItemBase | None = LogHistory.decode_line(_event("course@plan/task", 0))
    assert item is not None
    repo.logger.store(item)
    assert (tmp_path / ".tko" / FORMAT_FILE).read_bytes() == FORMAT_BYTES
    require_current_task_data(tmp_path)


def test_cli_applies_by_default_and_supports_dry_run(tmp_path: Path) -> None:
    _workspace(tmp_path)
    _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@old", 0))
    runner: CliRunner = CliRunner()
    before: dict[str, bytes] = _snapshot(tmp_path)
    preview = runner.invoke(app, ["migrate", str(tmp_path), "--dry-run"])
    assert preview.exit_code == 0, preview.output
    assert "course@old -> course@plan/task" in preview.output
    assert _snapshot(tmp_path) == before
    applied = runner.invoke(app, ["migrate", str(tmp_path)])
    assert applied.exit_code == 0, applied.output
    assert "Backup" in applied.output
    compatible = runner.invoke(app, ["migrate", str(tmp_path), "--apply"])
    assert compatible.exit_code == 0, compatible.output
    assert "Dados já migrados." in compatible.output


@pytest.mark.parametrize("mapping", [
    {"course@old": "other@plan/task"},
    {"course@old": "course@../outside"},
    {"course@a": "course@b", "course@b": "course@a"},
])
def test_invalid_mapping_is_rejected(tmp_path: Path, mapping: dict[str, str]) -> None:
    path: Path = _write(tmp_path, "map.json", json.dumps(mapping))
    with pytest.raises(ValueError):
        read_mapping(path)


def test_current_marker_and_pending_migration_are_checked(tmp_path: Path) -> None:
    initialize_task_data(tmp_path)
    _write(tmp_path, f".tko/{PENDING_FILE}", "{}")
    with pytest.raises(MigrationRequiredError, match="--recover"):
        require_current_task_data(tmp_path)


def test_watchers_use_current_identity_for_migrated_physical_folder(tmp_path: Path) -> None:
    from tko.game.task import Task
    from tko.game.task_enums import EvalMode
    from tko.game.task_location import TaskLocation
    from tko.repository.audit_logger import AuditLogger
    from tko.repository.edit_logger import EditLogger

    class Events:
        def __init__(self) -> None:
            self.keys: list[str] = []

        def store(self, action: LogItemBase) -> None:
            self.keys.append(action.key)

    class Audits:
        def __init__(self) -> None:
            self.keys: list[str] = []

        def store(self, task_key: str, file_ts_list: list[tuple[Path, dt.datetime | None]]) -> tuple[bool, int]:
            self.keys.append(task_key)
            return True, len(file_ts_list)

    repo: Repository = Repository(tmp_path, RunSettings(), None, recursive_search=False)
    task: Task = Task()
    task.basic.source_name = "course"
    task.basic.key = "labs/task"
    task.location = TaskLocation(eval=EvalMode.DIFF, external_source=True)
    repo.game.tasks[task.basic.full_key] = task
    _write(tmp_path, "course/labs/task/README.md", "task")
    file: Path = _write(tmp_path, "course/labs/task/src/main.py", "solution")
    unknown: Path = _write(tmp_path, "course/unlisted/src/main.py", "unlisted")
    _write(tmp_path, "course/unlisted/README.md", "unlisted")
    events: Events = Events()
    audits: Audits = Audits()
    changes: dict[Path, dt.datetime] = {file: dt.datetime(2026, 9, 14), unknown: dt.datetime(2026, 9, 14)}
    EditLogger(repo, events).on_flush_events(changes)
    AuditLogger(repo, audits).on_flush_events(changes)
    assert events.keys == ["course@labs/task"]
    assert audits.keys == ["course@labs/task"]


@pytest.mark.parametrize("marker", [b'{"version": 5}', b'{"version": true}', b'broken'])
def test_unknown_or_corrupt_format_never_gets_overwritten(tmp_path: Path, marker: bytes) -> None:
    _workspace(tmp_path)
    path: Path = _write(tmp_path, f".tko/{FORMAT_FILE}", marker)
    with pytest.raises(MigrationRequiredError):
        require_current_task_data(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors
    with pytest.raises(ValueError):
        plan.apply()
    assert path.read_bytes() == marker


def test_new_history_file_invalidates_inspected_plan(tmp_path: Path) -> None:
    _workspace(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@old", 0))
    with pytest.raises(ValueError, match="changed"):
        plan.apply()
    assert not (tmp_path / ".tko/migrations").exists()


def test_history_and_backup_symlinks_are_rejected(tmp_path: Path) -> None:
    _workspace(tmp_path)
    outside: Path = tmp_path / "outside"
    outside.mkdir()
    link: Path = tmp_path / ".tko/track"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="Symlink"):
        TaskDataMigration(tmp_path).inspect()
    link.unlink()
    (tmp_path / ".tko/migrations").symlink_to(outside, target_is_directory=True)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    with pytest.raises(ValueError, match="Symlink"):
        plan.apply()
    assert list(outside.iterdir()) == []


def test_recovery_refuses_to_overwrite_later_changes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _workspace(tmp_path)
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@old", 0))
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    original_write = transaction.atomic_bytes

    def interrupted_write(path: Path, content: bytes) -> None:
        if path.name == FORMAT_FILE and path.parent == tmp_path / ".tko":
            raise OSError("stop")
        original_write(path, content)

    with monkeypatch.context() as patch:
        patch.setattr(transaction, "atomic_bytes", interrupted_write)
        with pytest.raises(OSError):
            plan.apply()
    log.write_text("a later edit")
    with pytest.raises(ValueError, match="File changed"):
        recover_migration(tmp_path)
    assert log.read_text() == "a later edit"
    assert (tmp_path / ".tko" / PENDING_FILE).exists()


def test_remote_source_uses_local_snapshot_without_materializing(tmp_path: Path) -> None:
    _workspace(tmp_path, "# Local\n")
    config: Path = tmp_path / ".tko/repository.toml"
    config.write_text(config.read_text() + '[profile.sources.remote]\nuri = "https://github.com/example/course/blob/main/index/README.md"\n')
    _write(tmp_path, "remote/index/README.md", "- [ ] `@old` [Task](plan/task/README.md)\n")
    _write(tmp_path, ".tko/log/2026-09-14.log", _event("remote@old", 0))
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert plan.mapping["remote@old"] == "remote@plan/task"
    assert _snapshot(tmp_path) == before


def test_nested_task_histories_use_longest_known_root(tmp_path: Path) -> None:
    _workspace(tmp_path, "- [ ] `@parent` [Parent](plan/task/README.md)\n- [ ] `@parent/child` [Child](plan/task/nested/README.md)\n")
    _write(tmp_path, ".tko/track/course/parent/main.jsonl", b"parent")
    _write(tmp_path, ".tko/track/course/parent/child/main.jsonl", b"child")
    TaskDataMigration(tmp_path).inspect().apply()
    assert (tmp_path / ".tko/track/course/plan/task/main.jsonl").read_bytes() == b"parent"
    assert (tmp_path / ".tko/track/course/plan/task/nested/main.jsonl").read_bytes() == b"child"


def test_invalid_yaml_cli_reports_error_without_mutation(tmp_path: Path) -> None:
    _write(tmp_path, ".tko/repository.yaml", "sources: [\n")
    before: dict[str, bytes] = _snapshot(tmp_path)
    result = CliRunner().invoke(app, ["migrate", str(tmp_path), "--apply"])
    assert result.exit_code == 1
    assert "Migração falhou: Invalid repository configuration" in result.output
    assert "Invalid repository configuration" in result.output
    assert _snapshot(tmp_path) == before


def test_malformed_csv_blocks_migration(tmp_path: Path) -> None:
    _workspace(tmp_path)
    _write(tmp_path, ".tko/history.csv", 'hash,2026-09-14 10:00:00,SELF,course@old,"unterminated')
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert any("Invalid CSV" in error for error in plan.errors)
    with pytest.raises(ValueError):
        plan.apply()
    assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("family", ["track", "audit"])
@pytest.mark.parametrize("layout", ["course@animal", "course/animal"])
def test_history_directory_discovers_labs_entry_without_legacy_metadata(
    tmp_path: Path, family: str, layout: str,
) -> None:
    _workspace(tmp_path, "- [ ] [Animal](labs/animal/README.md)\n")
    config: Path = tmp_path / ".tko/repository.toml"
    config.write_text(config.read_text() + '[state]\nselected = "course@animal"\npinned = ["course@animal"]\n')
    old: Path = _write(tmp_path, f".tko/{family}/{layout}/draft.py.json", b"original snapshot")
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@animal", 0))
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert plan.mapping["course@animal"] == "course@labs/animal"
    assert _snapshot(tmp_path) == before
    plan.apply()
    assert not old.exists()
    assert (tmp_path / f".tko/{family}/course/labs/animal/draft.py.json").read_bytes() == b"original snapshot"
    assert log.read_text() == _event("course@labs/animal", 0)
    assert '"course@labs/animal"' in config.read_text()
    assert TaskDataMigration(tmp_path).inspect().changes == []


def test_empty_legacy_history_directory_can_identify_old_logs(tmp_path: Path) -> None:
    _workspace(tmp_path, "- [ ] [Animal](labs/animal/README.md)\n")
    (tmp_path / ".tko/track/course@animal").mkdir(parents=True)
    _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@animal", 0))
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert plan.mapping["course@animal"] == "course@labs/animal"


@pytest.mark.parametrize("index", [
    "- [ ] [Animal](plan/animal/README.md)\n",
    "- [ ] [Animal](other/labs/animal/README.md)\n",
])
def test_history_directory_without_labs_entry_uses_labs_destination(tmp_path: Path, index: str) -> None:
    _workspace(tmp_path, index)
    _write(tmp_path, ".tko/track/course@animal/draft.py.json", b"snapshot")
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert plan.mapping["course@animal"] == "course@labs/animal"


def test_history_directory_from_another_source_uses_own_labs_destination(tmp_path: Path) -> None:
    _workspace(tmp_path, "# Course\n")
    config: Path = tmp_path / ".tko/repository.toml"
    config.write_text(config.read_text() + '[profile.sources.other]\nuri = "other.md"\n')
    _write(tmp_path, "other.md", "- [ ] [Animal](labs/animal/README.md)\n")
    _write(tmp_path, ".tko/track/course@animal/draft.py.json", b"snapshot")
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert plan.mapping["course@animal"] == "course@labs/animal"


@pytest.mark.parametrize("competing_entry", [
    "- [ ] `@animal` [Different](labs/different/README.md)\n",
])
def test_history_labs_convention_does_not_override_competing_identity(
    tmp_path: Path, competing_entry: str,
) -> None:
    _workspace(tmp_path, "- [ ] [Animal](labs/animal/README.md)\n" + competing_entry)
    _write(tmp_path, ".tko/track/course@animal/draft.py.json", b"snapshot")
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert any("Ambiguous key: course@animal" in error for error in plan.errors)


def test_explicit_map_overrides_discovered_labs_convention(tmp_path: Path) -> None:
    _workspace(tmp_path, "- [ ] [Animal](labs/animal/README.md)\n- [ ] [Other](labs/other/README.md)\n")
    _write(tmp_path, ".tko/track/course@animal/draft.py.json", b"snapshot")
    plan: MigrationPlan = TaskDataMigration(tmp_path, {"course@animal": "course@labs/other"}).inspect()
    assert plan.errors == []
    assert plan.mapping["course@animal"] == "course@labs/other"
    plan.apply()
    assert (tmp_path / ".tko/track/course/labs/other/draft.py.json").read_bytes() == b"snapshot"


@pytest.mark.parametrize("kind", ["EXEC", "SELF", "MOVE"])
def test_log_only_migrates_to_existing_labs_entry(tmp_path: Path, kind: str) -> None:
    _workspace(tmp_path, "- [ ] [Animal](labs/animal/README.md)\n")
    fields: str = ", mode:EDIT" if kind == "MOVE" else ""
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@animal", 0, kind, fields))
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert plan.mapping["course@animal"] == "course@labs/animal"
    assert not (tmp_path / ".tko/track").exists()
    assert not (tmp_path / ".tko/audit").exists()
    plan.apply()
    assert log.read_text() == _event("course@labs/animal", 0, kind, fields)
    assert TaskDataMigration(tmp_path).inspect().changes == []


def test_exact_index_key_takes_precedence_over_labs_fallback(tmp_path: Path) -> None:
    _workspace(tmp_path, "- [ ] [Original](animal/README.md)\n- [ ] [Other](labs/animal/README.md)\n")
    lines: str = _event("course@animal", 0) + _event("course@labs/animal", 2)
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", lines)
    _write(tmp_path, ".tko/track/course@animal/draft.py.json", b"snapshot")
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert plan.mapping["course@animal"] == "course@animal"
    plan.apply()
    assert log.read_text() == lines
    assert (tmp_path / ".tko/track/course/animal/draft.py.json").read_bytes() == b"snapshot"


def test_csv_and_state_use_labs_fallback_without_history_directories(tmp_path: Path) -> None:
    _workspace(tmp_path, "- [ ] [Animal](labs/animal/README.md)\n")
    config: Path = tmp_path / ".tko/repository.toml"
    config.write_text(config.read_text() + '[state]\nselected = "course@animal"\n')
    csv: Path = _write(tmp_path, ".tko/history.csv", 'hash,2026-09-14 10:00:00,SELF,course@animal,"{c: 50}"\n')
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    plan.apply()
    assert "course@labs/animal" in csv.read_text()
    assert "course@labs/animal" in config.read_text()


def _workspace_with_activity(root: Path, *, remote: bool = False) -> Path:
    uri: str = "https://github.com/example/course/blob/main/README.md" if remote else "course/README.md"
    _write(root, ".tko/repository.toml", f'version = "0.3"\n[profile]\nauthoring_source = "course"\n[profile.sources.course]\nuri = "{uri}"\n')
    _write(root, "course/README.md", "# Course\n- [ ] [Animal](labs/animal/README.md)\n")
    return _write(root, "course/animal/README.md", "Animal description\n").parent


@pytest.mark.parametrize("remote", [False, True])
def test_activity_tree_moves_with_logs_and_versions(tmp_path: Path, remote: bool) -> None:
    import os
    import stat

    old: Path = _workspace_with_activity(tmp_path, remote=remote)
    script: Path = _write(tmp_path, "course/animal/src/run.sh", "#!/bin/sh\necho animal\n")
    script.chmod(0o751)
    os.utime(script, ns=(1234567890000000000, 1234567890000000000))
    (old / "empty").mkdir()
    _write(tmp_path, "course/animal/.vscode/settings.json", "{}")
    _write(tmp_path, ".tko/track/course@animal/draft.py.json", b"track snapshot")
    _write(tmp_path, ".tko/audit/course@animal/draft.py.jsonl", b"audit snapshot")
    log: Path = _write(tmp_path, ".tko/log/2026-09-14.log", _event("course@animal", 0))
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert not plan.errors
    assert plan.moves == {"course/animal": "course/labs/animal"}
    assert _snapshot(tmp_path) == before
    backup: Path | None = plan.apply()
    assert backup is not None
    destination: Path = tmp_path / "course/labs/animal"
    assert not old.exists()
    assert (destination / "README.md").read_bytes() == before["course/animal/README.md"]
    assert (destination / "empty").is_dir()
    assert (destination / ".vscode/settings.json").read_text() == "{}"
    assert stat.S_IMODE((destination / "src/run.sh").stat().st_mode) == 0o751
    assert (destination / "src/run.sh").stat().st_mtime_ns == 1234567890000000000
    assert (backup / "before/course/animal/src/run.sh").read_bytes() == before["course/animal/src/run.sh"]
    assert (tmp_path / ".tko/track/course/labs/animal/draft.py.json").read_bytes() == b"track snapshot"
    assert (tmp_path / ".tko/audit/course/labs/animal/draft.py.jsonl").read_bytes() == b"audit snapshot"
    assert "course@labs/animal" in log.read_text()
    assert TaskDataMigration(tmp_path).inspect().apply() is None


@pytest.mark.parametrize("identical", [False, True])
def test_activity_destination_collision_never_overwrites_work(tmp_path: Path, identical: bool) -> None:
    old: Path = _workspace_with_activity(tmp_path)
    source: Path = _write(tmp_path, "course/animal/src/main.py", b"old work")
    destination: Path = _write(tmp_path, "course/labs/animal/src/main.py", b"old work" if identical else b"new work")
    _write(tmp_path, "course/labs/animal/notes.txt", b"keep")
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    if identical:
        assert not plan.errors
        plan.apply()
        assert not old.exists()
        assert destination.read_bytes() == b"old work"
        assert (tmp_path / "course/labs/animal/notes.txt").read_bytes() == b"keep"
    else:
        assert any("Conflicting activity files" in error for error in plan.errors)
        with pytest.raises(ValueError):
            plan.apply()
        assert source.read_bytes() == b"old work"
        assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("existing_destination", [False, True])
def test_recovery_restores_moved_activity_and_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, existing_destination: bool,
) -> None:
    import os
    import stat

    old: Path = _workspace_with_activity(tmp_path)
    script: Path = _write(tmp_path, "course/animal/run.sh", b"#!/bin/sh\necho old\n")
    script.chmod(0o755)
    os.utime(script, ns=(1234567890000000000, 1234567890000000000))
    (old / "empty").mkdir()
    if existing_destination:
        _write(tmp_path, "course/labs/animal/notes.txt", b"existing destination")
    before: dict[str, bytes] = _snapshot(tmp_path)
    dirs_before: set[str] = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_dir()}
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    original_write = transaction.atomic_bytes

    def fail_marker(path: Path, content: bytes) -> None:
        if path == tmp_path / ".tko" / FORMAT_FILE:
            raise OSError("interrupted after moving activity")
        original_write(path, content)

    with monkeypatch.context() as patch:
        patch.setattr(transaction, "atomic_bytes", fail_marker)
        with pytest.raises(OSError, match="interrupted"):
            plan.apply()
    assert not old.exists()
    recover_migration(tmp_path)
    restored: dict[str, bytes] = {name: data for name, data in _snapshot(tmp_path).items() if not name.startswith(".tko/migrations/")}
    assert restored == before
    dirs_after: set[str] = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_dir() and not p.is_relative_to(tmp_path / ".tko/migrations")}
    assert dirs_after == dirs_before
    assert stat.S_IMODE(script.stat().st_mode) == 0o755
    assert script.stat().st_mtime_ns == 1234567890000000000
    TaskDataMigration(tmp_path).inspect().apply()
    assert not old.exists()


def test_prior_identity_migration_requires_directory_upgrade(tmp_path: Path) -> None:
    _workspace_with_activity(tmp_path)
    marker: Path = _write(tmp_path, f".tko/{FORMAT_FILE}", b'{"version": 1}\n')
    with pytest.raises(MigrationRequiredError, match="Pastas de atividades"):
        require_current_task_data(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert not plan.errors
    plan.apply()
    assert marker.read_bytes() == FORMAT_BYTES
    require_current_task_data(tmp_path)
    assert not (tmp_path / "course/animal").exists()


def test_prior_track_format_requires_jsonl_upgrade(tmp_path: Path) -> None:
    _workspace(tmp_path)
    marker: Path = _write(tmp_path, f".tko/{FORMAT_FILE}", b'{"version": 2}\n')
    _write(tmp_path, ".tko/track/course/plan/task/track.csv", "2026-09-14_10-00-00,100%,\n")
    with pytest.raises(MigrationRequiredError, match="Dados de tarefas"):
        require_current_task_data(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    plan.apply()
    assert marker.read_bytes() == FORMAT_BYTES
    assert (tmp_path / ".tko/track/course/plan/task/track.jsonl").is_file()
    require_current_task_data(tmp_path)


def test_activity_files_added_after_preview_block_application(tmp_path: Path) -> None:
    _workspace_with_activity(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    _write(tmp_path, "course/animal/new.txt", b"new work")
    with pytest.raises(ValueError, match="Activity directory changed"):
        plan.apply()
    assert not (tmp_path / ".tko/migrations").exists()


def test_activity_symlinks_block_migration_without_following_them(tmp_path: Path) -> None:
    old: Path = _workspace_with_activity(tmp_path)
    outside: Path = _write(tmp_path, "outside.txt", b"outside")
    (old / "linked.txt").symlink_to(outside)
    with pytest.raises(ValueError, match="Symlink"):
        TaskDataMigration(tmp_path).inspect()
    assert outside.read_bytes() == b"outside"


def test_directory_only_activity_can_be_moved(tmp_path: Path) -> None:
    old: Path = _workspace_with_activity(tmp_path)
    (old / "README.md").unlink()
    (old / "empty").mkdir()
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    plan.apply()
    assert not old.exists()
    assert (tmp_path / "course/labs/animal/empty").is_dir()


def test_cli_reports_activity_move_in_dry_run(tmp_path: Path) -> None:
    _workspace_with_activity(tmp_path)
    result = CliRunner().invoke(app, ["migrate", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "move directory: course/animal -> course/labs/animal" in result.output
    assert (tmp_path / "course/animal").is_dir()
    assert not (tmp_path / "course/labs/animal").exists()


def test_recovery_handles_partial_activity_file_transfer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    old: Path = _workspace_with_activity(tmp_path)
    _write(tmp_path, "course/animal/src/main.py", b"work")
    before: dict[str, bytes] = _snapshot(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    original_write = transaction.atomic_bytes

    def fail_destination(path: Path, content: bytes) -> None:
        if path == tmp_path / "course/labs/animal/src/main.py":
            raise OSError("interrupted during transfer")
        original_write(path, content)

    with monkeypatch.context() as patch:
        patch.setattr(transaction, "atomic_bytes", fail_destination)
        with pytest.raises(OSError, match="interrupted"):
            plan.apply()
    assert old.is_dir()
    recover_migration(tmp_path)
    restored: dict[str, bytes] = {name: data for name, data in _snapshot(tmp_path).items() if not name.startswith(".tko/migrations/")}
    assert restored == before
    assert not (tmp_path / "course/labs").exists()


def test_recovery_refuses_new_files_inside_moved_activity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _workspace_with_activity(tmp_path)
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    original_write = transaction.atomic_bytes

    def fail_marker(path: Path, content: bytes) -> None:
        if path == tmp_path / ".tko" / FORMAT_FILE:
            raise OSError("interrupted")
        original_write(path, content)

    with monkeypatch.context() as patch:
        patch.setattr(transaction, "atomic_bytes", fail_marker)
        with pytest.raises(OSError):
            plan.apply()
    later: Path = _write(tmp_path, "course/labs/animal/later.txt", b"new work")
    with pytest.raises(ValueError, match="File added after migration"):
        recover_migration(tmp_path)
    assert later.read_bytes() == b"new work"


def test_nested_legacy_activity_directories_move_to_their_own_destinations(tmp_path: Path) -> None:
    _workspace_with_activity(tmp_path)
    _write(tmp_path, "course/README.md", "- [ ] `@parent` [Parent](labs/parent/README.md)\n- [ ] `@parent/child` [Child](labs/child/README.md)\n")
    _write(tmp_path, "course/parent/README.md", b"parent")
    _write(tmp_path, "course/parent/child/README.md", b"child")
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert not plan.errors
    plan.apply()
    assert (tmp_path / "course/labs/parent/README.md").read_bytes() == b"parent"
    assert (tmp_path / "course/labs/child/README.md").read_bytes() == b"child"
    assert not (tmp_path / "course/parent").exists()


def test_activity_move_skips_directory_containing_an_existing_index(tmp_path: Path) -> None:
    _workspace(tmp_path)
    config: Path = tmp_path / ".tko/repository.toml"
    config.write_text(config.read_text() + '[profile.sources.nested]\nuri = "course/old/index.md"\n')
    index: Path = _write(tmp_path, "course/old/index.md", "# Nested index\n")
    plan: MigrationPlan = TaskDataMigration(tmp_path).inspect()
    assert plan.errors == []
    assert "course/old" not in plan.moves
    plan.apply()
    assert index.read_text() == "# Nested index\n"
