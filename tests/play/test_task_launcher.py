from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from tko.floating.floating import Floating, FloatingType
from tko.play.task_launcher import TaskLauncher


class _DummyFloatingManager:
    def __init__(self) -> None:
        self.items: list[Floating] = []

    def add_floating(self, item: Floating) -> None:
        self.items.append(item)


def test_run_selected_task_reports_missing_task_file(tmp_path: Path) -> None:
    missing_readme = tmp_path / "missing" / "README.md"
    fman = _DummyFloatingManager()
    repo = SimpleNamespace(
        task_resolver=SimpleNamespace(
            target_file=lambda _task: missing_readme,
            target_folder=lambda _task: missing_readme.parent,
        ),
        data=SimpleNamespace(lang="py"),
    )
    launcher = TaskLauncher(
        repo=cast(Any, repo),
        settings=cast(Any, SimpleNamespace()),
        fman=cast(Any, fman),
        tree=cast(Any, SimpleNamespace()),
        gui=cast(Any, SimpleNamespace()),
        downloader=cast(Any, SimpleNamespace()),
        editor=cast(Any, SimpleNamespace()),
    )

    launcher.run_selected_task(cast(Any, SimpleNamespace()))

    assert len(fman.items) == 1
    assert fman.items[0].type == FloatingType.ERROR
    text = "\n".join(line.plain() for line in fman.items[0].content)
    assert "A tarefa não existe" in text
    assert str(missing_readme) in text
