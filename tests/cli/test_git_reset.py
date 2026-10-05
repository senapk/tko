"""The batch reset replaces local repository contents with origin."""

from __future__ import annotations

import subprocess
from pathlib import Path

from tko.git.reset_remote import RemoteReset, ResetResult


def _git(directory: Path, *args: str) -> str:
    result: subprocess.CompletedProcess[str] = subprocess.run(
        ["git", "-C", str(directory), *args],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _repository(tmp_path: Path) -> tuple[Path, Path]:
    remote: Path = tmp_path / "remote.git"
    seed: Path = tmp_path / "seed"
    seed.mkdir()
    _git(tmp_path, "init", "--bare", "--initial-branch=main", str(remote))
    _git(seed, "init", "--initial-branch=main")
    _git(seed, "config", "user.name", "Teacher")
    _git(seed, "config", "user.email", "teacher@example.test")
    (seed / "work.txt").write_text("remote version\n", encoding="utf-8")
    _git(seed, "add", "-A")
    _git(seed, "commit", "-m", "remote commit")
    _git(seed, "remote", "add", "origin", str(remote))
    _git(seed, "push", "-u", "origin", "main")
    student: Path = tmp_path / "student"
    _git(tmp_path, "clone", str(remote), str(student))
    return student, remote


def test_reset_removes_tracked_untracked_and_ignored_changes(tmp_path: Path) -> None:
    student, remote = _repository(tmp_path)
    (student / "work.txt").write_text("local version\n", encoding="utf-8")
    (student / "new.txt").write_text("untracked\n", encoding="utf-8")
    (student / ".git" / "info" / "exclude").write_text("ignored.txt\n", encoding="utf-8")
    (student / "ignored.txt").write_text("ignored\n", encoding="utf-8")

    result: ResetResult = RemoteReset.reset(student)

    assert result.success, result.message
    assert (student / "work.txt").read_text(encoding="utf-8") == "remote version\n"
    assert not (student / "new.txt").exists()
    assert not (student / "ignored.txt").exists()
    assert _git(student, "rev-parse", "HEAD") == _git(remote, "rev-parse", "main")
    assert _git(student, "status", "--porcelain") == ""


def test_reset_discards_local_commits_and_fetches_remote(tmp_path: Path) -> None:
    student, remote = _repository(tmp_path)
    _git(student, "config", "user.name", "Student")
    _git(student, "config", "user.email", "student@example.test")
    (student / "local.txt").write_text("local commit\n", encoding="utf-8")
    _git(student, "add", "-A")
    _git(student, "commit", "-m", "local commit")
    (tmp_path / "seed" / "remote.txt").write_text("new remote work\n", encoding="utf-8")
    _git(tmp_path / "seed", "add", "-A")
    _git(tmp_path / "seed", "commit", "-m", "new remote work")
    _git(tmp_path / "seed", "push")

    result: ResetResult = RemoteReset.reset(student)

    assert result.success, result.message
    assert not (student / "local.txt").exists()
    assert (student / "remote.txt").read_text(encoding="utf-8") == "new remote work\n"
    assert _git(student, "rev-parse", "HEAD") == _git(remote, "rev-parse", "main")


def test_reset_reports_missing_repository(tmp_path: Path) -> None:
    result: ResetResult = RemoteReset.reset(tmp_path / "missing")

    assert not result.success
    assert "Diretório não encontrado" in result.message
