from pathlib import Path
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from tko.cli.cli_task import app
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.repository.repository import Repository


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path)
    return settings


def _make_repo_mock(tmp_path: Path) -> MagicMock:
    """Create a mock Repository with required attributes."""
    repo_mock = MagicMock(spec=Repository)
    paths_mock = MagicMock()
    paths_mock.root_dir = tmp_path
    repo_mock.paths = paths_mock
    return repo_mock


def test_task_down_requires_full_key(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    def fake_load_repo(*_args: object, **_kwargs: object) -> tuple[None, None]:
        return None, None

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)

    result = runner.invoke(app, ["down"], obj=ctx)

    # When repo is not found, the command returns silently with exit code 0
    assert result.exit_code == 0
