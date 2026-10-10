"""The review entry point requires a class folder and never creates a repository."""

from __future__ import annotations

from pathlib import Path

from click.testing import Result
from pytest import MonkeyPatch
from typer.testing import CliRunner

from tko.__main__ import app
from tko.play.review import ReviewSession


def test_review_routes_parent_folder_without_initializing_it(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    visited: list[Path] = []

    def run(session: ReviewSession) -> None:
        visited.append(session.repositories[0].parent)

    child: Path = tmp_path / "student"
    (child / ".tko").mkdir(parents=True)
    (child / ".tko" / "repository.toml").write_text("[profile]\n", encoding="utf-8")
    monkeypatch.setattr(ReviewSession, "run", run)

    result: Result = CliRunner().invoke(app, ["-S", str(tmp_path / "settings"), "review", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert visited == [tmp_path]
    assert not (tmp_path / ".tko").exists()


def test_review_rejects_folder_without_student_repositories(tmp_path: Path) -> None:
    result: Result = CliRunner().invoke(app, ["-S", str(tmp_path / "settings"), "review", str(tmp_path)])

    assert result.exit_code == 2
    assert "Nenhum repositório TKO" in result.output
    assert not (tmp_path / ".tko").exists()
