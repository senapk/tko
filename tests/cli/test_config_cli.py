from pathlib import Path
from types import SimpleNamespace
from typing import Any

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from tko.cli.cli_config import app
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings


class _FakeRepositoryConfig:
    def __init__(self, repo: Any):
        self.repo = repo
        self.save_calls = 0

    def load(self):
        return self

    def save(self, force: bool = False):
        _ = force
        self.save_calls += 1
        return self


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path, local_cache=True)
    return settings


def test_config_audit_turns_on(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)
    repo = SimpleNamespace(data=SimpleNamespace(audit=SimpleNamespace(enabled=False)))
    holder: dict[str, _FakeRepositoryConfig] = {}

    def fake_load_repo(*_args: Any, **_kwargs: Any) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path

    def fake_repo_config(repo_arg: Any) -> _FakeRepositoryConfig:
        cfg = _FakeRepositoryConfig(repo_arg)
        holder["cfg"] = cfg
        return cfg

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.repository.repository_config.RepositoryConfig", fake_repo_config)

    result = runner.invoke(app, ["audit", "--on"], obj=ctx)

    assert result.exit_code == 0
    assert repo.data.audit.enabled is True
    assert holder["cfg"].save_calls == 1
    assert "ON" in result.output


def test_config_audit_turns_off(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)
    repo = SimpleNamespace(data=SimpleNamespace(audit=SimpleNamespace(enabled=True)))
    holder: dict[str, _FakeRepositoryConfig] = {}

    def fake_load_repo(*_args: Any, **_kwargs: Any) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path

    def fake_repo_config(repo_arg: Any) -> _FakeRepositoryConfig:
        cfg = _FakeRepositoryConfig(repo_arg)
        holder["cfg"] = cfg
        return cfg

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.repository.repository_config.RepositoryConfig", fake_repo_config)

    result = runner.invoke(app, ["audit", "--off"], obj=ctx)

    assert result.exit_code == 0
    assert repo.data.audit.enabled is False
    assert holder["cfg"].save_calls == 1
    assert "OFF" in result.output


def test_config_audit_rejects_on_and_off_together(tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    result = runner.invoke(app, ["audit", "--on", "--off"], obj=ctx)

    assert result.exit_code != 0
    assert "only one option" in result.output.lower()
