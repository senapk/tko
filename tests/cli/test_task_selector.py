from pathlib import Path
from types import SimpleNamespace

from tko.cli.task_selector import TaskSelector
from tko.game.task import Task
from tko.game.task_enums import EvalMode
from tko.game.task_location import TaskLocation
from tko.util.rt import RT


def make_task(index: Path, link: str, key: str, external: bool = False) -> Task:
    task = Task()
    task.basic.source_name = "course"
    task.basic.key = key
    task.location = TaskLocation(
        index_path=index,
        raw_link=link,
        eval=EvalMode.DIFF,
        external_source=external,
    )
    task.basic.title = key
    return task


def test_selector_prefers_task_containing_current_directory(tmp_path: Path, monkeypatch) -> None:
    folder = tmp_path / "labs" / "carro"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text("# Carro\n", encoding="utf-8")
    task = make_task(tmp_path / "README.md", "labs/carro/README.md", "labs/carro")
    repo = SimpleNamespace(
        game=SimpleNamespace(tasks={task.basic.full_key: task}),
        task_resolver=SimpleNamespace(target_folder=lambda _task: None),
        paths=SimpleNamespace(root_dir=tmp_path),
    )
    monkeypatch.chdir(folder)

    assert TaskSelector(repo).select() is task


def test_selector_downloadable_excludes_existing_external_task(tmp_path: Path) -> None:
    folder = tmp_path / "course" / "labs" / "carro"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text("# Carro\n", encoding="utf-8")
    task = make_task(tmp_path / "course" / "README.md", "labs/carro/README.md", "labs/carro", external=True)
    repo = SimpleNamespace(
        game=SimpleNamespace(tasks={task.basic.full_key: task}),
        task_resolver=SimpleNamespace(target_folder=lambda _task: folder),
        paths=SimpleNamespace(root_dir=tmp_path),
    )

    assert TaskSelector(repo)._eligible_tasks("downloadable") == []


def test_selector_preserves_tree_colors_for_terminal_selectors(tmp_path: Path, monkeypatch) -> None:
    task = make_task(tmp_path / "README.md", "labs/carro/README.md", "labs/carro")
    (tmp_path / "labs" / "carro").mkdir(parents=True)
    (tmp_path / "labs" / "carro" / "README.md").write_text("# Carro\n", encoding="utf-8")
    repo = SimpleNamespace(
        game=SimpleNamespace(tasks={task.basic.full_key: task}),
        task_resolver=SimpleNamespace(target_folder=lambda _task: None),
        paths=SimpleNamespace(root_dir=tmp_path),
    )

    class Tree:
        def get_rendered_items(self, show_selected: bool):
            del show_selected
            return [(RT("colored task", "g"), task)]

    class CmdOpen:
        def __init__(self, _settings, _repo):
            pass

        def build_tree(self, **_kwargs):
            return Tree()

    monkeypatch.setattr("tko.cmds.cmd_open.CmdOpen", CmdOpen)
    settings = SimpleNamespace(rs=SimpleNamespace(monochrome=False))

    rendered = TaskSelector(repo, settings)._rendered_tasks([task])[task.basic.full_key]

    assert "\033[" in rendered
