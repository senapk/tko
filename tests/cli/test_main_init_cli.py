from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner
import typer

from tko.cli.cli_main import register_main_commands
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path, local_cache=True)
    return settings


def test_init_passes_audit_flag_to_repository_starter(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    app = typer.Typer()
    register_main_commands(app)
    ctx = _make_app_context(tmp_path)

    captured: dict[str, object] = {"execute": False}

    class DummyStarter:
        def __init__(
            self,
            settings: Settings,
            language: str | None,
            skip_add_remote: bool,
            force_location: bool = False,
            audit_enabled: bool = False,
        ):
            captured["settings"] = settings
            captured["language"] = language
            captured["skip_add_remote"] = skip_add_remote
            captured["force_location"] = force_location
            captured["audit_enabled"] = audit_enabled

        def execute(self) -> bool:
            captured["execute"] = True
            return True

    monkeypatch.setattr("tko.repository.repository_starter.RepositoryStarter", DummyStarter)

    result = runner.invoke(app, ["init", "--skip-remotes", "--audit", "--language", "py"], obj=ctx)

    assert result.exit_code == 0
    assert captured["settings"] is ctx
    assert captured["language"] == "py"
    assert captured["skip_add_remote"] is True
    assert captured["audit_enabled"] is True
    assert captured["execute"] is True
