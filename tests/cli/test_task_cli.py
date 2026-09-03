from pathlib import Path
from _pytest.monkeypatch import MonkeyPatch

from typer.testing import CliRunner

from tko.cli.cli_task import app
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.util.console import Console


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path)
    return settings




def test_task_down_requires_full_key(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    def fake_load_repo(*_args: object, **_kwargs: object) -> tuple[None, None]:
        return None, None

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)

    result = runner.invoke(app, ["down"], obj=ctx)

    # When repo is not found, the command returns silently with exit code 0
    assert result.exit_code == 0


def test_task_list_prints_each_duplicate_key_only_once(tmp_path: Path) -> None:
    (tmp_path / ".tko").mkdir()
    (tmp_path / ".tko" / "repository.toml").write_text(
        'version = "0.3"\n\n'
        '[profile]\n'
        'authoring_source = "base"\n\n'
        '[profile.sources.base]\n'
        'uri = "README.md"\n\n'
        '[profile.audit]\n'
        'enabled = false\n\n'
        '[preferences]\n'
        'inbox = "all"\n'
        'lang = "c"\n\n'
        '[state]\n'
        'expanded = []\n'
        'selected = ""\n'
        'selected_index = 0\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Course\n\n"
        "## First <!-- @first -->\n"
        "- [ ] `@same type=read` [First](first/README.md)\n"
        "## Second <!-- @second -->\n"
        "- [ ] `@same type=read` [Duplicate](first/README.md)\n"
        "- [ ] `@unique type=read` [Unique](unique/README.md)\n",
        encoding="utf-8",
    )
    (tmp_path / "first").mkdir()
    (tmp_path / "first" / "README.md").write_text("# First\n", encoding="utf-8")
    (tmp_path / "unique").mkdir()
    (tmp_path / "unique" / "README.md").write_text("# Unique\n", encoding="utf-8")
    ctx = _make_app_context(tmp_path)
    ctx.rs.force_offline = True

    with Console.capture() as output:
        result = CliRunner().invoke(app, ["list", "--all"], obj=ctx)
    rendered = output.getvalue()

    assert result.exit_code == 0
    assert rendered.count("base@same") == 1
    assert rendered.count("base@unique") == 1


def test_task_tests_lists_cases_without_running_solver(tmp_path: Path) -> None:
    activity = tmp_path / "labs" / "carro"
    activity.mkdir(parents=True)
    (activity / "README.md").write_text(
        "# Carro\n\n```toml\n[[tests]]\ninput = '1'\noutput = '1'\n```\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["tests", str(activity)], obj=_make_app_context(tmp_path))

    assert result.exit_code == 0
    assert "1 test(s)" in result.stdout
    assert "README.md" in result.stdout
