from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner
import typer

from tko.cli.cli_main import register_main_commands
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path)
    return settings


def test_init_passes_arguments_to_repository_starter(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
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
            profile_uri: str | None = None,
        ):
            captured["settings"] = settings
            captured["language"] = language
            captured["skip_add_remote"] = skip_add_remote
            captured["force_location"] = force_location
            captured["profile_uri"] = profile_uri

        def execute(self) -> bool:
            captured["execute"] = True
            return True

    monkeypatch.setattr("tko.repository.repository_starter.RepositoryStarter", DummyStarter)

    result = runner.invoke(app, ["init", "--skip-sources", "--language", "py"], obj=ctx)

    assert result.exit_code == 0
    assert captured["settings"] is ctx
    assert captured["language"] == "py"
    assert captured["skip_add_remote"] is True
    assert captured["profile_uri"] is None
    assert captured["execute"] is True


def test_init_passes_profile_to_repository_starter(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    app = typer.Typer()
    register_main_commands(app)
    ctx = _make_app_context(tmp_path)

    captured: dict[str, object] = {}

    class DummyStarter:
        def __init__(
            self,
            settings: Settings,
            language: str | None,
            skip_add_remote: bool,
            force_location: bool = False,
            profile_uri: str | None = None,
        ):
            captured["profile_uri"] = profile_uri
            captured["skip_add_remote"] = skip_add_remote

        def execute(self) -> bool:
            return True

    monkeypatch.setattr("tko.repository.repository_starter.RepositoryStarter", DummyStarter)

    result = runner.invoke(app, ["init", "--profile", "profile.toml"], obj=ctx)

    assert result.exit_code == 0
    assert captured == {"profile_uri": "profile.toml", "skip_add_remote": False}
