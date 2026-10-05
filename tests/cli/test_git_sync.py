"""End-to-end behavior of the student Git synchronization command."""

from __future__ import annotations

import subprocess
from pathlib import Path

from click.testing import Result
from pytest import MonkeyPatch
from typer.testing import CliRunner

from tko.__main__ import app
from tko.config.user_data import UserData


def _git(cwd: Path, *args: str) -> str:
    result: subprocess.CompletedProcess[str] = subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repository(tmp_path: Path) -> tuple[Path, Path]:
    remote: Path = tmp_path / "remote.git"
    seed: Path = tmp_path / "seed"
    seed.mkdir()
    _git(tmp_path, "init", "--bare", "--initial-branch=main", str(remote))
    _git(seed, "init", "--initial-branch=main")
    _git(seed, "config", "user.name", "Student")
    _git(seed, "config", "user.email", "student@example.test")
    (seed / "work.txt").write_text("initial\n", encoding="utf-8")
    _git(seed, "add", "-A")
    _git(seed, "commit", "-m", "initial")
    _git(seed, "remote", "add", "origin", str(remote))
    _git(seed, "push", "-u", "origin", "main")
    student: Path = tmp_path / "student"
    _git(tmp_path, "clone", str(remote), str(student))
    _git(student, "config", "user.name", "Student")
    _git(student, "config", "user.email", "student@example.test")
    return student, remote


def _invoke(tmp_path: Path, directory: Path, input_text: str = "", language: str = "pt") -> Result:
    return CliRunner().invoke(
        app,
        ["-S", str(tmp_path / "settings"), "--ui-language", language,
         "-C", str(directory), "git", "sync"],
        input=input_text,
    )


def test_git_sync_requires_repository(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    data_dir: Path = tmp_path / "data"
    monkeypatch.setattr(UserData, "settings_dir", lambda: data_dir)
    result: Result = _invoke(tmp_path, tmp_path, language="en")

    assert result.exit_code == 1
    assert "not a Git repository" in result.output
    assert list((data_dir / "git-sync" / "logs").glob("*.log"))


def test_git_sync_commits_and_pushes_without_staging_logs(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    student, remote = _repository(tmp_path)
    data_dir: Path = tmp_path / "data"
    monkeypatch.setattr(UserData, "settings_dir", lambda: data_dir)
    (student / "work.txt").write_text("student change\n", encoding="utf-8")

    result: Result = _invoke(tmp_path, student, "\nstudent work\n")

    assert result.exit_code == 0, result.output
    assert _git(student, "log", "-1", "--format=%s") == "student work"
    assert _git(remote, "log", "-1", "--format=%s", "main") == "student work"
    assert _git(student, "status", "--porcelain") == ""
    assert not (student / ".git_logs").exists()
    assert list((data_dir / "git-sync" / "logs").glob("*.log"))


def test_git_sync_declined_commit_does_not_fetch_or_push(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    student, remote = _repository(tmp_path)
    monkeypatch.setattr(UserData, "settings_dir", lambda: tmp_path / "data")
    (student / "work.txt").write_text("local change\n", encoding="utf-8")

    result: Result = _invoke(tmp_path, student, "n\n")

    assert result.exit_code == 0
    assert "Operação encerrada" in result.output
    assert _git(student, "status", "--porcelain") == "M work.txt"
    assert _git(remote, "log", "-1", "--format=%s", "main") == "initial"


def test_git_sync_receives_remote_fast_forward(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    student, remote = _repository(tmp_path)
    monkeypatch.setattr(UserData, "settings_dir", lambda: tmp_path / "data")
    other: Path = tmp_path / "other"
    _git(tmp_path, "clone", str(remote), str(other))
    _git(other, "config", "user.name", "Teacher")
    _git(other, "config", "user.email", "teacher@example.test")
    (other / "new.txt").write_text("new task\n", encoding="utf-8")
    _git(other, "add", "-A")
    _git(other, "commit", "-m", "new task")
    _git(other, "push")

    result: Result = _invoke(tmp_path, student)

    assert result.exit_code == 0, result.output
    assert (student / "new.txt").read_text(encoding="utf-8") == "new task\n"
    assert _git(student, "status", "--porcelain") == ""


def test_git_sync_rejects_other_branch(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    student, _remote = _repository(tmp_path)
    monkeypatch.setattr(UserData, "settings_dir", lambda: tmp_path / "data")
    _git(student, "switch", "-c", "exercise")

    result: Result = _invoke(tmp_path, student)

    assert result.exit_code == 1
    assert "Branch inválida: exercise" in result.output


def test_git_sync_requires_origin(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    student, _remote = _repository(tmp_path)
    monkeypatch.setattr(UserData, "settings_dir", lambda: tmp_path / "data")
    _git(student, "remote", "remove", "origin")

    result: Result = _invoke(tmp_path, student)

    assert result.exit_code == 1
    assert "Remoto 'origin' não configurado" in result.output


def test_git_sync_finishes_conflicted_merge_on_next_run(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    student, remote = _repository(tmp_path)
    monkeypatch.setattr(UserData, "settings_dir", lambda: tmp_path / "data")
    other: Path = tmp_path / "other"
    _git(tmp_path, "clone", str(remote), str(other))
    _git(other, "config", "user.name", "Teacher")
    _git(other, "config", "user.email", "teacher@example.test")
    (student / "work.txt").write_text("local\n", encoding="utf-8")
    _git(student, "add", "-A")
    _git(student, "commit", "-m", "local")
    (other / "work.txt").write_text("remote\n", encoding="utf-8")
    _git(other, "add", "-A")
    _git(other, "commit", "-m", "remote")
    _git(other, "push")

    conflicted: Result = _invoke(tmp_path, student)
    assert conflicted.exit_code == 0, conflicted.output
    assert "work.txt" in conflicted.output
    assert "versão local: git checkout --ours -- ." in conflicted.output
    assert "versão remota: git checkout --theirs -- ." in conflicted.output
    assert (student / ".git" / "MERGE_HEAD").exists()

    unresolved: Result = _invoke(tmp_path, student)
    assert unresolved.exit_code == 1
    assert "marcadores de conflito" in unresolved.output
    assert (student / ".git" / "MERGE_HEAD").exists()

    (student / "work.txt").write_text("resolved\n", encoding="utf-8")
    merged: Result = _invoke(tmp_path, student)
    assert merged.exit_code == 0, merged.output
    assert "Merge finalizado" in merged.output
    assert not (student / ".git" / "MERGE_HEAD").exists()

    pushed: Result = _invoke(tmp_path, student)
    assert pushed.exit_code == 0, pushed.output
    assert _git(remote, "show", "main:work.txt") == "resolved"
