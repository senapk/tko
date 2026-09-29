import base64
from pathlib import Path

import pytest
import tko.feno.build as build_module
from tko.feno.cases import Cases
from tko.cmds.cmd_build import CmdBuild


def test_build_all_moodle_embeds_local_files_and_writes_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "repo"
    task = root / "base" / "soma"
    src = task / "src" / "py"
    src.mkdir(parents=True)
    (task / "cover.png").write_bytes(b"cover-bytes")
    guide = task / "docs" / "guide.md"
    guide.parent.mkdir()
    guide.write_text("# Guide\n", encoding="utf-8")
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

    def fake_cases_run(cases_file: Path, source_readme: Path, source_dir: Path, settings: object) -> bool:
        _ = settings
        cases_file.write_text("case=sample\ninput=\noutput=\"\"\n", encoding="utf-8")
        return True

    monkeypatch.setattr(build_module.Cases, "run", staticmethod(fake_cases_run))
    monkeypatch.chdir(root)

    build_module.build_task(
        targets=[task],
        moodle=True,
        check=False,
        erase=False,
        brief=True,
    )

    readme = (task / ".cache" / "README.md").read_text(encoding="utf-8")
    cover_data: str = base64.b64encode(b"cover-bytes").decode("ascii")
    guide_data: str = base64.b64encode(b"# Guide\n").decode("ascii")
    assert f"![cover](data:image/png;base64,{cover_data})" in readme
    assert f"[guia](data:text/markdown;base64,{guide_data})" in readme
    assert "[pasta](docs/)" in readme
    html: str = (task / ".cache" / "README.html").read_text(encoding="utf-8")
    assert f"data:image/png;base64,{cover_data}" in html
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
        moodle=False,
        check=False,
        erase=False,
        brief=True,
    )

    assert calls == ["title", "cache", "recreate", "drafts", "local", "mdpp"]


def test_missing_local_asset_fails_moodle_target_and_removes_stale_html(
    tmp_path: Path,
) -> None:
    task: Path = tmp_path / "task"
    task.mkdir()
    (task / "README.md").write_text("# Task\n\n![missing](missing.png)\n", encoding="utf-8")
    cache: Path = task / ".cache"
    cache.mkdir()
    (cache / "README.md").write_text("stale\n", encoding="utf-8")
    (cache / "README.html").write_text("stale\n", encoding="utf-8")

    succeeded: bool = build_module.build_task(
        targets=[task], moodle=True, check=True, erase=False, brief=True
    )

    assert succeeded is False
    assert not (cache / "README.md").exists()
    assert not (cache / "README.html").exists()


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

    sources: list[Path] = []

    def fake_execute(command: CmdBuild) -> bool:
        sources.extend(command.source_list)
        return True

    monkeypatch.setattr("tko.cmds.cmd_build.CmdBuild.execute", fake_execute)

    Cases.run(tmp_path / "tests.vpl", source_readme, source_dir)

    assert source_dir / "tests.toml" in sources
    assert source_dir / "feedback.toml" not in sources
