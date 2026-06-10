from pathlib import Path
from types import SimpleNamespace
from typing import Any

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from tko.cli.cli_audit import app
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path, local_cache=True)
    return settings


def test_audit_starts_watcher_with_verbose_and_interval(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    repo = SimpleNamespace()
    captured: dict[str, Any] = {"stopped": False}

    def fake_load_repo(*_args: Any, **_kwargs: Any) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path

    class DummyWatcher:
        def __init__(self, _repo: object):
            captured["repo"] = _repo

        def start_watching(
            self,
            audit: bool | None = None,
            audit_verbose: bool = False,
            audit_interval_seconds: int | None = None,
        ) -> "DummyWatcher":
            captured["audit"] = audit
            captured["audit_verbose"] = audit_verbose
            captured["audit_interval_seconds"] = audit_interval_seconds
            return self

        def stop_watching(self) -> "DummyWatcher":
            captured["stopped"] = True
            return self

    def fake_sleep(_seconds: float) -> None:
        raise KeyboardInterrupt()

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.repository.repository_watcher.RepositoryWatcher", DummyWatcher)
    monkeypatch.setattr("time.sleep", fake_sleep)

    result = runner.invoke(app, ["--interval", "15"], obj=ctx)

    assert result.exit_code == 0
    assert captured["repo"] is repo
    assert captured["audit"] is True
    assert captured["audit_verbose"] is True
    assert captured["audit_interval_seconds"] == 15
    assert captured["stopped"] is True
    assert "Audit watcher started" in result.output
    assert "Audit watcher stopped" in result.output
