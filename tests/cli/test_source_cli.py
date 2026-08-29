from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import typer
from pytest import MonkeyPatch
from typer.testing import CliRunner

import tko.cli.cli_source as cli_source
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings


def make_settings(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path)
    return settings


def test_source_list_invokes_source_actions(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []
    repo = SimpleNamespace()
    def mock_load_repo(_rs: object) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path
    monkeypatch.setattr(cli_source, "load_repo", mock_load_repo)

    class FakeSourceActions:
        def __init__(self, settings: object, repo_arg: object) -> None:
            assert repo_arg is repo

        def list_sources(self):
            calls.append("list")

    monkeypatch.setattr(cli_source, "SourceActions", FakeSourceActions)

    result = CliRunner().invoke(cli_source.app, ["list"], obj=make_settings(tmp_path))

    assert result.exit_code == 0
    assert calls == ["list"]


def test_source_add_accepts_label_uri_and_authoring(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}
    repo = SimpleNamespace()
    def mock_load_repo(_rs: object) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path
    monkeypatch.setattr(cli_source, "load_repo", mock_load_repo)

    class FakeSourceActions:
        def __init__(self, settings: object, repo_arg: object) -> None:
            pass

        def add_source(self, label: str, uri: str, authoring: bool = False):
            captured.update(label=label, uri=uri, authoring=authoring)

    monkeypatch.setattr(cli_source, "SourceActions", FakeSourceActions)

    result = CliRunner().invoke(cli_source.app, ["add", "labs", "README.md", "--authoring"], obj=make_settings(tmp_path))

    assert result.exit_code == 0
    assert captured == {"label": "labs", "uri": "README.md", "authoring": True}


def test_source_set_authoring_invokes_action(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, str] = {}
    repo = SimpleNamespace()
    def mock_load_repo(_rs: object) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path
    monkeypatch.setattr(cli_source, "load_repo", mock_load_repo)

    class FakeSourceActions:
        def __init__(self, settings: object, repo_arg: object) -> None:
            pass

        def set_authoring_source(self, label: str):
            captured["label"] = label

    monkeypatch.setattr(cli_source, "SourceActions", FakeSourceActions)

    result = CliRunner().invoke(cli_source.app, ["set-authoring", "labs"], obj=make_settings(tmp_path))

    assert result.exit_code == 0
    assert captured == {"label": "labs"}


def test_source_set_uses_uri_option(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, str | None] = {}
    repo = SimpleNamespace()
    def mock_load_repo(_rs: object) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path
    monkeypatch.setattr(cli_source, "load_repo", mock_load_repo)

    class FakeSourceActions:
        def __init__(self, settings: object, repo_arg: object) -> None:
            pass

        def update_source(self, label: str, uri: str | None = None):
            captured.update(label=label, uri=uri)

    monkeypatch.setattr(cli_source, "SourceActions", FakeSourceActions)

    result = CliRunner().invoke(cli_source.app, ["set", "labs", "--uri", "outro/README.md"], obj=make_settings(tmp_path))

    assert result.exit_code == 0
    assert captured == {"label": "labs", "uri": "outro/README.md"}


def test_source_rm_invokes_action(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, str] = {}
    repo = SimpleNamespace()
    def mock_load_repo(_rs: object) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path
    monkeypatch.setattr(cli_source, "load_repo", mock_load_repo)

    class FakeSourceActions:
        def __init__(self, settings: object, repo_arg: object) -> None:
            pass

        def remove_source(self, label: str):
            captured["label"] = label

    monkeypatch.setattr(cli_source, "SourceActions", FakeSourceActions)

    result = CliRunner().invoke(cli_source.app, ["rm", "labs"], obj=make_settings(tmp_path))

    assert result.exit_code == 0
    assert captured == {"label": "labs"}


def test_source_help_does_not_announce_remote_group() -> None:
    app = typer.Typer()
    app.add_typer(cli_source.app, name="source")

    result = CliRunner().invoke(app, ["source", "--help"])

    assert result.exit_code == 0
    assert "Manage task sources" in result.output
    assert "remote task source" not in result.output.lower()


def test_root_help_announces_source_not_remote() -> None:
    from tko.__main__ import app

    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "source" in result.output
    assert "remote" not in result.output


def test_config_help_does_not_announce_sandbox_command() -> None:
    from tko.cli.cli_config import app

    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "sandbox" not in result.output
