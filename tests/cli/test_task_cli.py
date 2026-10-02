from pathlib import Path
from _pytest.monkeypatch import MonkeyPatch

from typer.testing import CliRunner

from tko.cli.cli_task import app
from tko.cli.cli_build import app as build_app
from tko.cli.cli_task import app as tko_task_app
from tko.cli.cli_tests import app as tests_app
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.enums.diff_count import DiffCount
from tko.util.console import Console


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path)
    return settings


def test_task_build_moves_to_build_group() -> None:
    assert "build" not in {command.name for command in app.registered_commands}
    assert {"task", "index", "download"} == {command.name for command in build_app.registered_commands}


def test_task_build_uses_moodle_flag_without_url(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    received: dict[str, tuple[object, ...]] = {}

    def fake_build_task(*args: object) -> bool:
        received["args"] = args
        return True

    monkeypatch.setattr("tko.feno.build.build_task", fake_build_task)

    result = CliRunner().invoke(
        build_app,
        ["task", "task", "--moodle"],
        obj=_make_app_context(tmp_path),
    )

    assert result.exit_code == 0
    assert received["args"][:5] == ([Path("task")], True, False, False, False)


def test_task_build_returns_failure_when_target_build_fails(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    def fake_build_task(*_args: object) -> bool:
        return False

    monkeypatch.setattr("tko.feno.build.build_task", fake_build_task)
    result = CliRunner().invoke(
        build_app, ["task", "task", "--moodle"], obj=_make_app_context(tmp_path)
    )

    assert result.exit_code == 1


def test_task_check_runs_sorted_languages_for_each_activity(
    monkeypatch: MonkeyPatch, tmp_path: Path,
) -> None:
    first: Path = tmp_path / "first"
    second: Path = tmp_path / "second"
    (first / "src" / "zlang").mkdir(parents=True)
    (first / "src" / "alang").mkdir(parents=True)
    (second / "src" / "clang").mkdir(parents=True)
    calls: list[dict[str, object]] = []

    class FakeRun:
        def __init__(self, **kwargs: object) -> None:
            calls.append(kwargs)

        def execute(self) -> int:
            return 100

    monkeypatch.setattr("tko.cli.cli_task.load_repo", lambda *_args, **_kwargs: (object(), None))
    monkeypatch.setattr("tko.cmds.cmd_run.Run", FakeRun)

    result = CliRunner().invoke(
        app, ["check", str(first), str(second)], obj=_make_app_context(tmp_path),
    )

    assert result.exit_code == 0, result.output
    assert [call["language"] for call in calls] == ["alang", "zlang", "clang"]
    assert all(call["target_list"] in ([first.resolve()], [second.resolve()]) for call in calls)
    assert all(getattr(call["param"], "compact") for call in calls)
    assert all(getattr(call["param"], "diff_count") == DiffCount.NONE for call in calls)


def test_task_check_continues_after_failure_and_returns_error(
    monkeypatch: MonkeyPatch, tmp_path: Path,
) -> None:
    activity: Path = tmp_path / "activity"
    (activity / "src" / "cpp").mkdir(parents=True)
    (activity / "src" / "py").mkdir()
    results: dict[str, int] = {"cpp": 0, "py": 100}
    executed: list[str] = []

    class FakeRun:
        def __init__(self, **kwargs: object) -> None:
            language: object = kwargs["language"]
            assert isinstance(language, str)
            self.language: str = language

        def execute(self) -> int:
            executed.append(self.language)
            return results[self.language]

    monkeypatch.setattr("tko.cli.cli_task.load_repo", lambda *_args, **_kwargs: (object(), None))
    monkeypatch.setattr("tko.cmds.cmd_run.Run", FakeRun)

    result = CliRunner().invoke(app, ["check", str(activity)], obj=_make_app_context(tmp_path))

    assert result.exit_code == 1
    assert executed == ["cpp", "py"]


def test_task_check_reports_missing_languages(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    activity: Path = tmp_path / "activity"
    activity.mkdir()
    monkeypatch.setattr("tko.cli.cli_task.load_repo", lambda *_args, **_kwargs: (object(), None))

    result = CliRunner().invoke(app, ["check", str(activity)], obj=_make_app_context(tmp_path))

    assert result.exit_code == 1
    assert "Nenhuma linguagem encontrada" in result.output




def test_task_download_requires_repository(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    def fake_load_repo(*_args: object, **_kwargs: object) -> tuple[None, None]:
        return None, None

    monkeypatch.setattr("tko.cli.cli_task.load_repo", fake_load_repo)

    result = runner.invoke(tko_task_app, ["down"], obj=ctx)

    assert result.exit_code == 1


def test_task_tests_lists_cases_without_running_solver(tmp_path: Path) -> None:
    activity = tmp_path / "labs" / "carro"
    activity.mkdir(parents=True)
    (activity / "README.md").write_text(
        "# Carro\n\n```toml\n[[tests]]\ninput = '1'\noutput = '1'\n```\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(tests_app, ["list", str(activity)])

    assert result.exit_code == 0
    assert "1 test(s)" in result.stdout
    assert "README.md" in result.stdout
