from pathlib import Path
from typing import Any

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner
import typer

from tko.cli.cli_main import register_main_commands
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.util.console import Console


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
        def __init__(self, _settings: Settings, _repo: object, _watcher: object):
            captured["settings"] = _settings
            captured["repo"] = _repo
            captured["cmd_watcher"] = _watcher

        def execute(self) -> None:
            captured["execute"] = True

    class DummyWatcher:
        def __init__(self, _repo: object):
            captured["watcher_repo"] = _repo

        def start_watching(
            self,
            log_edits: bool = True,
            log_audit: bool = False,
            audit_verbose: bool = False,
            audit_interval_seconds: int | None = None,
        ) -> "DummyWatcher":
            captured["log_edits"] = log_edits
            captured["log_audit"] = log_audit
            captured["audit_verbose"] = audit_verbose
            captured["audit_interval_seconds"] = audit_interval_seconds
            return self

        def stop_watching(self) -> "DummyWatcher":
            captured["stopped"] = True
            return self

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.cmds.cmd_open.CmdOpen", DummyCmdOpen)
    monkeypatch.setattr("tko.repository.repository_watcher.RepositoryWatcher", DummyWatcher)

    with Console.capture() as out:
        result = runner.invoke(app, ["open"], obj=ctx)
    _ = out.getvalue()

    assert result.exit_code == 0
    assert captured["settings"] is ctx
    assert captured["repo"] is repo_obj
    assert captured["watcher_repo"] is repo_obj
    assert captured["cmd_watcher"] is not None
    assert captured["log_edits"] is True
    assert captured["log_audit"] is False
    assert captured["audit_verbose"] is True
    assert captured["audit_interval_seconds"] is None
    assert captured["execute"] is True
    assert captured["stopped"] is True
