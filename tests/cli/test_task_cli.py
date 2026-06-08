from pathlib import Path
from _pytest.monkeypatch import MonkeyPatch

from typer.testing import CliRunner

from tko.cli.cli_task import app
from tko.config.settings import Settings
from tko.repository.git_cache import UpdateMode
from tko.repository.repository import Repository


def test_task_down_requires_full_key(tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    result = runner.invoke(app, ["down"], obj=ctx)

    assert result.exit_code != 0
    assert "Missing argument" in result.output


def test_task_down_invokes_cmd_down_with_full_key(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)
    repo_obj = object()
    calls: dict[str, object] = {"execute": False}

    def fake_load_repo(*_args: object, **_kwargs: object) -> tuple[object, Path, UpdateMode]:
        return repo_obj, tmp_path, UpdateMode.IF_OLDER

    class DummyCmdDown:
        def __init__(self, repo: Repository, task_key: str, settings: Settings):
            calls["repo"] = repo
            calls["task_key"] = task_key
            calls["settings"] = settings

        def execute(self):
            calls["execute"] = True
            return True

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.cmds.cmd_down.CmdDown", DummyCmdDown)

    result = runner.invoke(app, ["down", "fup@mumia"], obj=ctx)

    assert result.exit_code == 0
    assert calls["repo"] is repo_obj
    assert calls["task_key"] == "fup@mumia"
    assert calls["settings"] is ctx.settings
    assert calls["execute"] is True


def test_task_down_returns_when_repo_not_found(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    def fake_load_repo(*_args: object, **_kwargs: object) -> tuple[None, None, UpdateMode]:
        return None, None, UpdateMode.IF_OLDER

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)

    result = runner.invoke(app, ["down", "fup@mumia"], obj=ctx)

    assert result.exit_code == 0


def test_task_down_handles_domain_errors(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)
    repo_obj = object()

    def fake_load_repo(*_args: object, **_kwargs: object) -> tuple[object, Path, UpdateMode]:
        return repo_obj, tmp_path, UpdateMode.IF_OLDER

    class DummyCmdDown:
        def __init__(self, _repo: Repository, _task_key: str, _settings: Settings):
            raise Warning("fail: tarefa 'fup@x' não encontrada no curso")

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.cmds.cmd_down.CmdDown", DummyCmdDown)

    result = runner.invoke(app, ["down", "fup@x"], obj=ctx)

    assert result.exit_code == 1
    assert "não encontrada no curso" in result.output
