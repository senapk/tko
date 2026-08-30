from pathlib import Path
from types import SimpleNamespace

from tko.floating.floating import Floating, FloatingType
from tko.game.task import Task
from tko.play.task_launcher import TaskLauncher


class _DummyFloatingManager:
    def __init__(self) -> None:
        self.items: list[Floating] = []

    def add_floating(self, item: Floating) -> None:
        self.items.append(item)


def test_run_selected_task_reports_missing_task_file(tmp_path: Path) -> None:
    missing_readme = tmp_path / "missing" / "README.md"
    fman = _DummyFloatingManager()

    def target_file(_task: Task) -> Path:
        return missing_readme

    def target_folder(_task: Task) -> Path:
        return missing_readme.parent

    repo = SimpleNamespace(
        task_resolver=SimpleNamespace(
            target_file=target_file,
            target_folder=target_folder,
        ),
        data=SimpleNamespace(lang="py"),
    )
    launcher = TaskLauncher(
        repo=repo,  # type: ignore[arg-type]
        settings=SimpleNamespace(),  # type: ignore[arg-type]
        fman=fman,  # type: ignore[arg-type]
        tree=SimpleNamespace(),  # type: ignore[arg-type]
        gui=SimpleNamespace(),  # type: ignore[arg-type]
        downloader=SimpleNamespace(),  # type: ignore[arg-type]
        editor=SimpleNamespace(),  # type: ignore[arg-type]
    )

    launcher.run_selected_task(SimpleNamespace())  # type: ignore[arg-type]

    assert len(fman.items) == 1
    assert fman.items[0].type == FloatingType.ERROR
    text = "\n".join(line.plain() for line in fman.items[0].content)
    assert "A tarefa não existe" in text
    assert str(missing_readme) in text
