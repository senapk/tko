from pathlib import Path
import subprocess

import pytest
import tko.feno.build as build_module
from tko.feno.cases import Cases


def test_build_all_moodle_writes_rebased_readme_and_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "repo"
    task = root / "base" / "soma"
    src = task / "src" / "py"
    src.mkdir(parents=True)
    (task / "README.md").write_text(
        "# Soma\n\n"
        "![cover](cover.png)\n"
        "[guia](docs/guide.md)\n"
        "[pasta](docs/)\n",
        encoding="utf-8",
    )
    (src / "solver.py").write_text(
        'print("visible") # @KEEP\n'
        "# @DROP\n"
        'print("hidden")\n',
        encoding="utf-8",
    )

    def fake_cases_run(cases_file: Path, source_readme: Path, source_dir: Path) -> None:
        cases_file.write_text("case=sample\ninput=\noutput=\"\"\n", encoding="utf-8")

    monkeypatch.setattr(build_module.Cases, "run", staticmethod(fake_cases_run))
    monkeypatch.chdir(root)

    build_module.build_task(
        targets=[task],
        remote_url="https://github.com/user/repo/tree/main",
        check=False,
        erase=False,
        brief=True,
    )

    readme = (task / ".cache" / "README.md").read_text(encoding="utf-8")
    assert (
        "![cover](https://raw.githubusercontent.com/user/repo/main/base/soma/cover.png)"
        in readme
    )
    assert (
        "[guia](https://github.com/user/repo/blob/main/base/soma/docs/guide.md)"
        in readme
    )
    assert "[pasta](https://github.com/user/repo/tree/main/base/soma/docs/)" in readme
    assert (task / ".cache" / "README.html").is_file()
    assert (task / ".cache" / "tests.vpl").is_file()
    assert (task / ".cache" / "starter" / "py" / "solver.py").read_text(
        encoding="utf-8"
    ) == 'print("visible")\n'
    assert not (task / ".cache" / "mapi.json").exists()


def test_build_runs_mdpp_only_after_local_steps(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    task = tmp_path / "task"
    task.mkdir()
    calls: list[str] = []

    monkeypatch.setattr(build_module.Actions, "load_title", lambda _self: calls.append("title"))
    monkeypatch.setattr(build_module.Actions, "create_cache", lambda _self: calls.append("cache"))
    monkeypatch.setattr(build_module.Actions, "recreate_cache", lambda _self: calls.append("recreate"))
    monkeypatch.setattr(build_module.Actions, "copy_drafts", lambda _self: calls.append("drafts"))
    monkeypatch.setattr(build_module.Actions, "run_local_sh", lambda _self: calls.append("local"))
    monkeypatch.setattr(build_module.Actions, "update_markdown", lambda _self: calls.append("mdpp"))

    build_module.build_task(
        targets=[task],
        remote_url=None,
        check=False,
        erase=False,
        brief=True,
    )

    assert calls == ["title", "cache", "recreate", "drafts", "local", "mdpp"]


def test_moodle_rebuild_requires_every_published_artifact(tmp_path: Path) -> None:
    task = tmp_path / "task"
    source = task / "src" / "py"
    source.mkdir(parents=True)
    (task / "README.md").write_text("# Task\n", encoding="utf-8")
    (source / "main.py").write_text("print(1)\n", encoding="utf-8")

    actions = build_module.Actions(task)
    actions.cache.mkdir()
    actions.output_readme.write_text("# Task\n", encoding="utf-8")
    actions.output_html.write_text("<h1>Task</h1>\n", encoding="utf-8")
    actions.output_cases.write_text("case\n", encoding="utf-8")
    (actions.output_starter / "py").mkdir(parents=True)
    (actions.output_starter / "py" / "main.py").write_text("print(1)\n", encoding="utf-8")

    assert actions.need_rebuild(moodle=True) is False

    actions.output_html.unlink()

    assert actions.need_rebuild(moodle=True) is True


def test_cases_excludes_feedback_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source_dir = tmp_path / "task"
    source_dir.mkdir()
    source_readme = source_dir / "README.md"
    source_readme.write_text("# Task\n", encoding="utf-8")
    (source_dir / "tests.toml").write_text("[[tests]]\n", encoding="utf-8")
    (source_dir / "feedback.toml").write_text("[feedback]\n", encoding="utf-8")

    commands: list[list[str]] = []

    def fake_run(command: list[str], *, stdout: int, check: bool) -> None:
        _ = stdout
        _ = check
        commands.append(command)

    monkeypatch.setattr(subprocess, "run", fake_run)

    Cases.run(tmp_path / "tests.vpl", source_readme, source_dir)

    assert len(commands) == 1
    assert str(source_dir / "tests.toml") in commands[0]
    assert str(source_dir / "feedback.toml") not in commands[0]
