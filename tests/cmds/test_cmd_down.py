from pathlib import Path
from types import SimpleNamespace

from tko.cmds.cmd_down import CmdDown
from tko.config.settings import Settings
from tko.game.task import Task
from tko.game.task_enums import TaskType
from tko.game.task_location import TaskLocation


def test_external_read_materializes_markdown_and_assets_without_tests_or_drafts(tmp_path: Path) -> None:
    origin = tmp_path / "origin"
    destination = tmp_path / "workspace" / "source" / "reading"
    (origin / "assets").mkdir(parents=True)
    (origin / "README.md").write_text("# Reading\n\n[notes](notes.md)\n", encoding="utf-8")
    (origin / "notes.md").write_text("# Notes\n", encoding="utf-8")
    (origin / "assets" / "cover.png").write_bytes(b"png")
    (origin / "tests.toml").write_text("[tests]\n", encoding="utf-8")

    task = Task()
    task.basic.key = "reading"
    task.basic.source_name = "source"
    task.location = TaskLocation(
        index_path=origin / "index.md",
        raw_link="README.md",
        task_type=TaskType.READ,
        external_source=True,
    )

    repo = SimpleNamespace(
        game=SimpleNamespace(get_task_throw=lambda _key: task),
        task_resolver=SimpleNamespace(
            origin_file=lambda _task, load_git: (origin / "README.md"),
            target_folder=lambda _task: destination,
        ),
        data=SimpleNamespace(lang="py"),
    )
    settings = Settings(None)

    assert CmdDown(repo, "@reading", settings).execute() is True
    assert (destination / "README.md").exists()
    assert (destination / "notes.md").exists()
    assert (destination / "assets" / "cover.png").exists()
    assert not (destination / "tests.toml").exists()
    assert not any(destination.glob("draft.*"))
