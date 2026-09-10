from pathlib import Path
from types import SimpleNamespace

from tko.floating.floating import Floating, FloatingType
from tko.game.task import Task
from tko.play.task_launcher import TaskLauncher
from tko.config.settings import Settings


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


class _RunWithoutSolver:
    def __init__(self, **_kwargs: object) -> None:
        self.context = SimpleNamespace(wdir=SimpleNamespace(solver=None))

    def set_opener(self, _opener: object) -> "_RunWithoutSolver":
        return self

    def set_run_without_ask(self, _value: bool) -> "_RunWithoutSolver":
        return self

    def set_curses(self, _value: bool) -> "_RunWithoutSolver":
        return self

    def set_task(self, _repo: object, _task: object) -> "_RunWithoutSolver":
        return self

    def load(self) -> "_RunWithoutSolver":
        return self


def test_run_selected_local_task_without_solver_creates_default_draft(tmp_path: Path, monkeypatch) -> None:
    task_folder = tmp_path / "task"
    task_folder.mkdir()
    (task_folder / "README.md").write_text("# Task\n", encoding="utf-8")
    fman = _DummyFloatingManager()
    task = SimpleNamespace(
        basic=SimpleNamespace(full_key="source@task"),
        location=SimpleNamespace(is_external=False),
    )
    repo = SimpleNamespace(
        task_resolver=SimpleNamespace(
            target_file=lambda _task: task_folder / "README.md",
            target_folder=lambda _task: task_folder,
        ),
        data=SimpleNamespace(lang="py"),
    )

    monkeypatch.setattr("tko.play.task_launcher.Run", _RunWithoutSolver)

    class _UnexpectedCmdDown:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("local tasks must not be downloaded")

    monkeypatch.setattr("tko.play.task_launcher.CmdDown", _UnexpectedCmdDown)
    launcher = TaskLauncher(
        repo=repo,  # type: ignore[arg-type]
        settings=Settings(None),
        fman=fman,  # type: ignore[arg-type]
        tree=SimpleNamespace(),  # type: ignore[arg-type]
        gui=SimpleNamespace(watcher=None),  # type: ignore[arg-type]
        downloader=SimpleNamespace(),  # type: ignore[arg-type]
        editor=SimpleNamespace(),  # type: ignore[arg-type]
    )

    launcher.run_selected_task(task)  # type: ignore[arg-type]

    draft = task_folder / "src" / "py" / "draft.py"
    assert draft.read_text(encoding="utf-8") == "# Escreva seu código aqui\nprint('Hello, World!')"


def test_run_selected_external_task_without_solver_downloads_drafts(tmp_path: Path, monkeypatch) -> None:
    task_folder = tmp_path / "task"
    task_folder.mkdir()
    (task_folder / "README.md").write_text("# Task\n", encoding="utf-8")
    task = SimpleNamespace(
        basic=SimpleNamespace(full_key="source@task"),
        location=SimpleNamespace(is_external=True),
    )
    repo = SimpleNamespace(
        task_resolver=SimpleNamespace(
            target_file=lambda _task: task_folder / "README.md",
            target_folder=lambda _task: task_folder,
        ),
        data=SimpleNamespace(lang="py"),
    )
    calls: list[tuple[object, str, object]] = []

    class _CmdDown:
        def __init__(self, received_repo: object, task_key: str, settings: object) -> None:
            calls.append((received_repo, task_key, settings))

        def execute(self) -> bool:
            return True

    monkeypatch.setattr("tko.play.task_launcher.Run", _RunWithoutSolver)
    monkeypatch.setattr("tko.play.task_launcher.CmdDown", _CmdDown)
    settings = Settings(None)
    launcher = TaskLauncher(
        repo=repo,  # type: ignore[arg-type]
        settings=settings,
        fman=_DummyFloatingManager(),  # type: ignore[arg-type]
        tree=SimpleNamespace(),  # type: ignore[arg-type]
        gui=SimpleNamespace(watcher=None),  # type: ignore[arg-type]
        downloader=SimpleNamespace(),  # type: ignore[arg-type]
        editor=SimpleNamespace(),  # type: ignore[arg-type]
    )

    launcher.run_selected_task(task)  # type: ignore[arg-type]

    assert calls == [(repo, "source@task", settings)]
