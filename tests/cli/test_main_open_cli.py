from pathlib import Path
from typing import Any

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner
import typer

from tko.cli.cli_main import register_main_commands
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path, local_cache=True)
    settings.rs.force_offline = True
    return settings


def test_open_starts_non_audit_watcher(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    app = typer.Typer()
    register_main_commands(app)
    ctx = _make_app_context(tmp_path)

    repo_obj = object()
    captured: dict[str, Any] = {"execute": False, "stopped": False}

    def fake_load_repo(*_args: Any, **_kwargs: Any) -> tuple[object, Path]:
        return repo_obj, tmp_path

    class DummyCmdOpen:
        def __init__(self, _settings: Settings, _repo: object):
            captured["settings"] = _settings
            captured["repo"] = _repo

        def execute(self) -> None:
            captured["execute"] = True

    class DummyWatcher:
        def __init__(self, _repo: object):
            captured["watcher_repo"] = _repo

        def start_watching(self, audit: bool | None = None) -> "DummyWatcher":
            captured["audit"] = audit
            return self

        def stop_watching(self) -> "DummyWatcher":
            captured["stopped"] = True
            return self

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.cmds.cmd_open.CmdOpen", DummyCmdOpen)
    monkeypatch.setattr("tko.repository.repository_watcher.RepositoryWatcher", DummyWatcher)

    result = runner.invoke(app, ["open"], obj=ctx)

    assert result.exit_code == 0
    assert captured["settings"] is ctx
    assert captured["repo"] is repo_obj
    assert captured["watcher_repo"] is repo_obj
    assert captured["audit"] is False
    assert captured["execute"] is True
    assert captured["stopped"] is True
