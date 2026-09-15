"""Behavioral coverage of the unified CLI and its path contracts."""
from pathlib import Path

import pytest
from click.testing import Result
from typer.main import get_command
from typer.testing import CliRunner

from tko.__main__ import app
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.enums.diff_mode import DiffMode
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader
from tko.repository.remote import Source
from tko.repository.source_actions import SourceActions
from tko.repository.task_data_format import FORMAT_BYTES, FORMAT_FILE
from tko.util.console import Console
from tko.util.param import Param


def workspace(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / ".tko").mkdir()
    (root / ".tko" / "repository.toml").write_text(
        'version = "0.3"\n[profile]\nauthoring_source = "course"\n'
        '[profile.sources.course]\nuri = "README.md"\n', encoding="utf-8",
    )
    (root / ".tko" / FORMAT_FILE).write_bytes(FORMAT_BYTES)
    (root / "README.md").write_text('# Course\n## Tasks\n- [ ] `eval=diff` [Task](labs/task/README.md)\n')
    activity: Path = root / "labs/task"
    activity.mkdir(parents=True)
    (activity / "README.md").write_text('# Task\n\n```toml\n[[tests]]\ninput = "1"\noutput = "2"\n```\n')
    (activity / "nested").mkdir()
    (activity / "nested/solver.py").write_text("print(2)\n")
    return activity


def invoke(root: Path, args: list[str], input: str | None = None) -> Result:
    return CliRunner().invoke(app, ["-S", str(root / "settings"), "-O", *args], input=input)


def test_command_tree_has_only_canonical_names() -> None:
    from click import Group

    root = get_command(app)
    assert isinstance(root, Group)
    expected: dict[str, set[str]] = {
        "task": {"build", "show", "open", "list", "tests", "download"},
        "collect": {"repo", "tasks", "skills"},
            "config": {"set", "list", "reset", "clear-cache", "self-update", "uninstall", "source", "profile", "audit"},
        "tool": {"mdpp", "convert-tests", "older", "diff", "rebase", "filter", "html", "migrate", "pull"},
    }
    assert not {"util", "reset", "cache", "profile", "source", "self-update", "uninstall", "class"} & root.commands.keys()
    for name, children in expected.items():
        group = root.commands[name]
        assert isinstance(group, Group)
        assert set(group.commands) == children

    config = root.commands["config"]
    assert isinstance(config, Group)
    for name, children in {"source": {"list", "add", "remove", "set"}, "profile": {"link", "status", "update", "unlink"}}.items():
        group = config.commands[name]
        assert isinstance(group, Group)
        assert set(group.commands) == children


@pytest.mark.parametrize("args", [
    ["util"], ["reset"], ["cache", "clear"], ["profile", "status"], ["source", "list"], ["self-update"], ["uninstall"], ["class"], ["class", "pull"], ["task", "down"], ["collect", "task"], ["class", "tasks"],
    ["class", "skills"], ["source", "rm"], ["source", "set-authoring"], ["tool", "tests"],
    ["--lang", "pt"], ["run", "--lang", "py"], ["run", "--side"], ["run", "--down"],
    ["run", "--none"], ["run", "--all"], ["run", "-f"], ["init", "--skip-remotes"],
    ["tool", "migrate", "--apply"], ["tool", "diff", "a", "b", "--text"],
    ["tool", "diff", "a", "b", "--path"], ["tool", "rebase", "x", "--relative", "y"],
    ["config", "set", "--side"], ["task", "list", "--down"],
])
def test_removed_interfaces_are_rejected(tmp_path: Path, args: list[str]) -> None:
    assert invoke(tmp_path, args).exit_code == 2


@pytest.mark.parametrize("args", [
    ["run", "--diff-mode", "invalid"], ["run", "--failures", "invalid"],
    ["task", "open", "--diff-mode", "invalid"], ["config", "set", "--diff-mode", "invalid"],
    ["tool", "diff", "a", "b", "--input-type", "invalid"], ["config", "source", "set", "course"],
])
def test_invalid_options_are_rejected(tmp_path: Path, args: list[str]) -> None:
    assert invoke(tmp_path, args).exit_code == 2


@pytest.mark.parametrize("relative", [False, True])
def test_changedir_controls_migration_and_restores_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: bool) -> None:
    workspace(tmp_path / "repo")
    marker: Path = tmp_path / "repo/.tko" / FORMAT_FILE
    marker.unlink()
    monkeypatch.chdir(tmp_path)
    selected: str = "repo" if relative else str(tmp_path / "repo")
    preview: Result = invoke(tmp_path, ["-C", selected, "tool", "migrate", "--dry-run"])
    assert preview.exit_code == 0, preview.output
    assert not marker.exists()
    result: Result = invoke(tmp_path, ["-C", selected, "tool", "migrate"])
    assert result.exit_code == 0, result.output
    assert marker.read_bytes() == FORMAT_BYTES
    assert Path.cwd() == tmp_path


def test_changedir_preserves_settings_base_and_restores_on_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    activity: Path = workspace(tmp_path / "repo")
    monkeypatch.chdir(tmp_path)
    result: Result = CliRunner().invoke(app, ["-S", "settings", "-C", "repo", "config", "set", "--diff-mode", "down"])
    assert result.exit_code == 0, result.output
    settings: Settings = Settings(tmp_path / "settings")
    settings.load_settings()
    assert settings.app.diff_mode == DiffMode.DOWN
    assert not (tmp_path / "repo/settings").exists()
    failed: Result = invoke(tmp_path, ["-C", str(activity), "task", "show", "missing"])
    assert failed.exit_code == 2
    assert Path.cwd() == tmp_path
    missing_dir: Result = invoke(tmp_path, ["-C", "missing", "task", "list"])
    assert missing_dir.exit_code == 2
    assert Path.cwd() == tmp_path


@pytest.mark.parametrize("relative_path", ["labs/task", "labs/task/README.md", "labs/task/nested/solver.py"])
def test_show_resolves_explicit_activity_paths(tmp_path: Path, relative_path: str) -> None:
    workspace(tmp_path / "repo")
    with Console.capture() as output:
        result: Result = invoke(tmp_path, ["-C", str(tmp_path / "repo"), "task", "show", relative_path])
    assert result.exit_code == 0, result.output
    assert "Task: course@labs/task" in output.getvalue()
    assert "Select an element" not in result.output


def test_show_absolute_path_finds_repository_from_outside(tmp_path: Path) -> None:
    activity: Path = workspace(tmp_path / "repo")
    with Console.capture() as output:
        result: Result = invoke(tmp_path, ["-C", str(tmp_path), "task", "show", str(activity)])
    assert result.exit_code == 0, result.output
    assert "Task: course@labs/task" in output.getvalue()


@pytest.mark.parametrize("command", ["show", "tests"])
def test_current_subdirectory_and_root_selection(tmp_path: Path, command: str) -> None:
    activity: Path = workspace(tmp_path / "repo")
    current: Result = invoke(tmp_path, ["-C", str(activity / "nested"), "task", command])
    assert current.exit_code == 0, current.output
    assert "Select an element" not in current.output
    selected: Result = invoke(tmp_path, ["-C", str(tmp_path / "repo"), "task", command], input="1\n")
    assert selected.exit_code == 0, selected.output
    assert "Select an element" in selected.output
    cancelled: Result = invoke(tmp_path, ["-C", str(tmp_path / "repo"), "task", command], input="q\n")
    assert cancelled.exit_code == 0
    assert "No materialized task selected" in cancelled.output


def test_fzf_explicitly_overrides_current_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    activity: Path = workspace(tmp_path / "repo")
    calls: list[list[tuple[str, str]]] = []

    def choose(elements: list[tuple[str, str]], pattern: str | None = None, selected: str | None = None) -> str:
        calls.append(elements)
        return elements[0][0]

    monkeypatch.setattr("tko.cli.task_selector.select_with_fzf", choose)
    result: Result = invoke(tmp_path, ["-C", str(activity), "task", "tests", "--fzf"])
    assert result.exit_code == 0, result.output
    assert len(calls) == 1
    assert "1 test(s)" in result.output


@pytest.mark.parametrize("command", ["show", "open", "tests"])
def test_paths_cannot_be_combined_with_fzf(tmp_path: Path, command: str) -> None:
    activity: Path = workspace(tmp_path / "repo")
    result: Result = invoke(tmp_path, ["task", command, str(activity), "--fzf"])
    assert result.exit_code == 2
    assert "cannot be combined" in result.output
    missing: Result = invoke(tmp_path, ["task", command, str(tmp_path / "missing")])
    assert missing.exit_code == 2


def test_tests_accepts_multiple_standalone_paths(tmp_path: Path) -> None:
    first: Path = workspace(tmp_path / "repo1") / "README.md"
    second: Path = workspace(tmp_path / "repo2") / "README.md"
    result: Result = invoke(tmp_path, ["-C", str(tmp_path), "task", "tests", str(first), str(second)])
    assert result.exit_code == 0, result.output
    assert result.output.count("1 test(s)") == 2


def test_graph_only_does_not_print_task_details(tmp_path: Path) -> None:
    activity: Path = workspace(tmp_path / "repo")
    with Console.capture() as output:
        result: Result = invoke(tmp_path, ["task", "show", str(activity), "--graph-only"])
    assert result.exit_code == 0, result.output
    assert "Task:" not in output.getvalue() and "Files:" not in output.getvalue()


@pytest.mark.parametrize("explicit", [False, True])
def test_task_open_uses_paths_and_diff_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, explicit: bool) -> None:
    activity: Path = workspace(tmp_path / "repo")
    observed: list[tuple[list[Path], DiffMode, bool]] = []

    class FakeRun:
        def __init__(self, settings: Settings, target_list: list[Path], param: Param.Basic, language: str | None, repo: Repository) -> None:
            observed.append((target_list, param.diff_mode, param.filter))
        def set_task(self, rep: Repository, task: Task) -> None:
            assert task.basic.full_key == "course@labs/task"
        def set_tui(self) -> None:
            pass
        def execute(self) -> None:
            pass

    monkeypatch.setattr("tko.cmds.cmd_run.Run", FakeRun)
    args: list[str] = ["-C", str(activity), "task", "open", "--filter", "--diff-mode", "down"]
    if explicit:
        args.extend(["README.md", "nested/solver.py"])
    result: Result = invoke(tmp_path, args)
    assert result.exit_code == 0, result.exception
    expected: list[Path] = [Path("README.md"), Path("nested/solver.py")] if explicit else [activity]
    assert observed == [(expected, DiffMode.DOWN, True)]


def test_source_combined_update_is_atomic(tmp_path: Path) -> None:
    repo: Repository = Repository(tmp_path / "repo", RunSettings(), None, recursive_search=False)
    settings: Settings = Settings(tmp_path / "settings")
    repo.data.set_source(Source.from_uri("second", "second/README.md"))
    RepositoryLoader(repo).save(force=True)
    original: bytes = repo.paths.config_file.read_bytes()
    outside: Path = tmp_path / "outside.md"
    outside.write_text("# External\n")
    actions: SourceActions = SourceActions(settings, repo)
    assert not actions.update_source("second", str(outside), authoring=True)
    assert repo.paths.config_file.read_bytes() == original
    source: Source | None = repo.data.get_source("second")
    assert source is not None and source.path_or_url == "second/README.md"
    assert repo.data.authoring_source == "labs"
    assert actions.update_source("second", "new/README.md", authoring=True)
    loaded: Repository = Repository(repo.root_dir, RunSettings(), None, recursive_search=False)
    RepositoryLoader(loaded).load()
    assert loaded.data.authoring_source == "second"
    updated: Source | None = loaded.data.get_source("second")
    assert updated is not None and updated.path_or_url == "new/README.md"


@pytest.mark.parametrize("failures", ["first", "all", "none"])
def test_run_propagates_explicit_options(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failures: str) -> None:
    from tko.enums.diff_count import DiffCount

    observed: list[tuple[DiffMode, DiffCount, bool, str | None]] = []

    class FakeRun:
        def __init__(self, settings: Settings, targets: list[Path], param: Param.Basic, language: str | None, repo: Repository | None) -> None:
            observed.append((param.diff_mode, param.diff_count, param.filter, language))
        def execute(self) -> None:
            pass

    monkeypatch.setattr("tko.cmds.cmd_run.Run", FakeRun)
    result: Result = invoke(tmp_path, ["-C", str(tmp_path), "run", "--language", "py", "--diff-mode", "down", "--failures", failures, "-F"])
    assert result.exit_code == 0, result.exception
    expected: dict[str, DiffCount] = {"first": DiffCount.FIRST, "all": DiffCount.ALL, "none": DiffCount.NONE}
    assert observed == [(DiffMode.DOWN, expected[failures], True, "py")]


def test_config_reset_restores_defaults(tmp_path: Path) -> None:
    changed: Result = invoke(tmp_path, ["config", "set", "--diff-mode", "down", "--editor", "custom-editor"])
    assert changed.exit_code == 0
    reset: Result = invoke(tmp_path, ["config", "reset"])
    assert reset.exit_code == 0, reset.output
    loaded: Settings = Settings(tmp_path / "settings")
    loaded.load_settings()
    defaults: Settings = Settings(None)
    assert loaded.app.diff_mode == defaults.app.diff_mode
    assert loaded.app.editor == defaults.app.editor


def test_cache_clear_only_removes_global_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache: Path = tmp_path / "cache"
    cache.mkdir()
    (cache / "cached-data").write_text("cached")
    activity: Path = workspace(tmp_path / "repo")

    def global_cache() -> Path:
        return cache

    monkeypatch.setattr("tko.config.user_data.UserData.global_cache_dir", global_cache)
    result: Result = invoke(tmp_path, ["config", "clear-cache"])
    assert result.exit_code == 0, result.output
    assert cache.is_dir() and list(cache.iterdir()) == []
    assert (activity / "README.md").is_file()


def test_collect_routes_reports_with_their_parameters(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[Path], str, str | None, str | None]] = []

    def tasks(rs: RunSettings, git_dir_list: list[Path], tasks_path: str) -> None:
        calls.append((git_dir_list, tasks_path, None, None))

    def skills(rs: RunSettings, git_dir_list: list[Path], skills_path: str, remote_index: str, prog_lang: str) -> None:
        calls.append((git_dir_list, skills_path, remote_index, prog_lang))

    monkeypatch.setattr("tko.collect.collect_many.CollectMany.load_tasks", tasks)
    monkeypatch.setattr("tko.collect.collect_many.CollectMany.load_skills", skills)
    task_result: Result = invoke(tmp_path, ["collect", "tasks", "student1", "student2", "--csv", "tasks.csv"])
    skill_result: Result = invoke(tmp_path, ["collect", "skills", "student1", "--csv", "skills.csv", "--source", "course", "--language", "py"])
    assert task_result.exit_code == skill_result.exit_code == 0
    assert calls == [([Path("student1"), Path("student2")], "tasks.csv", None, None), ([Path("student1")], "skills.csv", "course", "py")]


def test_collect_repo_requires_repository(tmp_path: Path) -> None:
    result: Result = invoke(tmp_path, ["-C", str(tmp_path), "collect", "repo", "--json"])
    assert result.exit_code == 1
    assert "No TKO repository found" in result.output


def test_tool_pull_routes_paths_and_threads(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    observed: list[tuple[list[Path], int]] = []

    def pull_all(paths: list[Path], threads: int) -> None:
        observed.append((paths, threads))

    monkeypatch.setattr("tko.collect.pull.Pull.pull_all_parallel", pull_all)
    result: Result = invoke(tmp_path, ["tool", "pull", "one", "two", "--threads", "4"])
    assert result.exit_code == 0, result.output
    assert observed == [([Path("one"), Path("two")], 4)]


def test_config_source_uses_selected_repository(tmp_path: Path) -> None:
    repo_dir: Path = tmp_path / "repo"
    workspace(repo_dir)
    added: Result = invoke(tmp_path, ["-C", str(repo_dir), "config", "source", "add", "extra", "extra/README.md"])
    assert added.exit_code == 0, added.output
    changed: Result = invoke(tmp_path, ["-C", str(repo_dir), "config", "source", "set", "extra", "--uri", "new/README.md", "--authoring"])
    assert changed.exit_code == 0, changed.output
    loaded: Repository = Repository(repo_dir, RunSettings(), None, recursive_search=False)
    RepositoryLoader(loaded).load()
    source: Source | None = loaded.data.get_source("extra")
    assert source is not None and source.path_or_url == "new/README.md"
    assert loaded.data.authoring_source == "extra"
    assert not (tmp_path / ".tko").exists()


def test_config_profile_uses_selected_repository(tmp_path: Path) -> None:
    repo_dir: Path = tmp_path / "repo"
    workspace(repo_dir)
    profile: Path = repo_dir / "profile.toml"
    profile.write_text(
        'version = "0.1"\nname = "Local profile"\nauthoring_source = "course"\n'
        'language = "py"\n[sources.course]\nuri = "README.md"\n', encoding="utf-8",
    )
    linked: Result = invoke(tmp_path, ["-C", str(repo_dir), "config", "profile", "link", "profile.toml"])
    assert linked.exit_code == 0, linked.output
    loaded: Repository = Repository(repo_dir, RunSettings(), None, recursive_search=False)
    RepositoryLoader(loaded).load()
    assert loaded.data.link is not None
    assert loaded.data.link.uri == str(profile)
    status: Result = invoke(tmp_path, ["-C", str(repo_dir), "config", "profile", "status"])
    assert status.exit_code == 0, status.output
    profile.write_text(profile.read_text().replace('language = "py"', 'language = "java"'))
    updated: Result = invoke(tmp_path, ["-C", str(repo_dir), "config", "profile", "update"])
    assert updated.exit_code == 0, updated.output
    RepositoryLoader(loaded).load()
    assert loaded.data.profile_language == "java"
    unlinked: Result = invoke(tmp_path, ["-C", str(repo_dir), "config", "profile", "unlink"])
    assert unlinked.exit_code == 0, unlinked.output
    RepositoryLoader(loaded).load()
    assert loaded.data.link is None
    assert loaded.data.profile_language == "java"
    assert not (tmp_path / ".tko").exists()
