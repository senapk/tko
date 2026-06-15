from datetime import datetime
from pathlib import Path

from tko.logger.audit_tracker import AuditTracker


class _FakePaths:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.config_folder = root_dir / ".tko"

    def get_audit_task_folder(self, label: str) -> Path:
        return self.root_dir / ".tko" / "audit" / label


class _FakeRepo:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.paths = _FakePaths(root_dir)

    def get_task_folder_for_label(self, label: str) -> Path:
        source, task = label.split("@", 1)
        return self.root_dir / source / task


def test_audit_tracker_stores_snapshots(tmp_path: Path) -> None:
    repo = _FakeRepo(tmp_path)
    task_folder = tmp_path / "disc" / "task01"
    src_lang_folder = task_folder / "src" / "py"
    src_lang_folder.mkdir(parents=True)
    (task_folder / "README.md").write_text("meta\n", encoding="utf-8")
    solver = src_lang_folder / "solver.py"
    solver.write_text("print('v1')\n", encoding="utf-8")
    timestamp = datetime(2026, 6, 9, 10, 11, 12)

    tracker = AuditTracker(repo, verbose=False, interval_seconds=0)  # type: ignore[arg-type]
    changed, total_lines = tracker.store("disc@task01", [(solver, timestamp)])

    assert changed is True
    assert total_lines == 1

    audit_folder = tmp_path / ".tko" / "audit" / "disc@task01"
    copied_file = audit_folder / "solver.py.jsonl"
    assert copied_file.exists()
    lines = copied_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1



def test_audit_tracker_ignores_files_outside_src_lang(tmp_path: Path) -> None:
    repo = _FakeRepo(tmp_path)
    task_folder = tmp_path / "disc" / "task03"
    task_folder.mkdir(parents=True)
    (task_folder / "README.md").write_text("meta\n", encoding="utf-8")
    outside = task_folder / "solver.py"
    outside.write_text("print('nope')\n", encoding="utf-8")

    tracker = AuditTracker(repo, verbose=False, interval_seconds=0)  # type: ignore[arg-type]
    changed, total_lines = tracker.store("disc@task03", [(outside, datetime(2026, 6, 9, 10, 11, 12))])

    assert changed is False
    assert total_lines == 0

    audit_folder = tmp_path / ".tko" / "audit" / "disc@task03"
    assert list(audit_folder.glob("*")) == [] if audit_folder.exists() else True


def test_audit_tracker_ignores_large_or_missing_files(tmp_path: Path) -> None:
    repo = _FakeRepo(tmp_path)
    task_folder = tmp_path / "disc" / "task02"
    src_lang_folder = task_folder / "src" / "py"
    src_lang_folder.mkdir(parents=True)
    (task_folder / "README.md").write_text("meta\n", encoding="utf-8")

    big_file = src_lang_folder / "big.txt"
    big_file.write_text("a" * 200, encoding="utf-8")
    missing = src_lang_folder / "missing.py"

    tracker = AuditTracker(repo, verbose=False, interval_seconds=0, max_file_size_bytes=64)  # type: ignore[arg-type]
    changed, total_lines = tracker.store("disc@task02", [(big_file, None), (missing, None)])

    assert changed is False
    assert total_lines == 0

    audit_folder = tmp_path / ".tko" / "audit" / "disc@task02"
    assert list(audit_folder.glob("*")) == [] if audit_folder.exists() else True
