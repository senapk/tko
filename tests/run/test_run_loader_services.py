from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tko.play.opener import Opener
from tko.run.filter_mode_service import FilterModeService
from tko.run.opener_factory import OpenerFactory
from tko.run.task_resolution_service import TaskResolutionService
from tko.run.wdir_bootstrap_service import WdirBootstrapService


class _FakeExecutable:
    def __init__(self):
        self.error: str | None = None

    def set_compile_error(self, msg: str):
        self.error = msg


class _FakeSolver:
    def __init__(self, args_list: list[Path] | None = None):
        self.args_list = [] if args_list is None else args_list
        self.exec = _FakeExecutable()

    def get_executable(self):
        return self.exec, True


class _FakeWdir:
    def __init__(self):
        self.calls: list[tuple[str, Any]] = []
        self._solver = _FakeSolver([Path("solver.py")])

    def set_curses(self, value: bool):
        self.calls.append(("set_curses", value))
        return self

    def set_lang(self, lang: str):
        self.calls.append(("set_lang", lang))
        return self

    def set_target_list(self, targets: list[Path]):
        self.calls.append(("set_target_list", targets))
        return self

    def build(self):
        self.calls.append(("build", None))
        return self

    def filter(self, param: Any):
        self.calls.append(("filter", param))
        return self

    def has_solver(self) -> bool:
        return True

    def get_solver(self):
        return self._solver


class _FailingWdir(_FakeWdir):
    def build(self):
        self.calls.append(("build", None))
        raise FileNotFoundError("x")


class _TaskViewRepo:
    def __init__(self, task: Any):
        self._task = task

    def get_task_from_task_folder(self, _pwd: Path):
        return self._task


def test_task_resolution_service_sets_task_from_repo():
    task = SimpleNamespace()
    ctx = SimpleNamespace(repo=_TaskViewRepo(task), pwd=Path("."), task=None)

    changed = TaskResolutionService.try_setup_task_from_repo(cast(Any, ctx))

    assert changed is True
    assert ctx.task is task


def test_task_resolution_service_sets_standalone_task_when_needed():
    ctx = SimpleNamespace(task=None, wdir_builded=True, track_folder=Path("x"))

    changed = TaskResolutionService.setup_task_from_wdir(cast(Any, ctx))

    assert changed is True
    assert ctx.task.basic.key == "STANDALONE"
    assert ctx.task.basic.remote_name == "NONE"
    assert ctx.track_folder is None


def test_filter_mode_service_keeps_only_existing_resolved_targets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    existing = tmp_path / "ok.tio"
    existing.write_text("", encoding="utf-8")
    missing = tmp_path / "missing.tio"

    monkeypatch.setattr("tko.run.filter_mode_service.TkoFilterMode.deep_copy_and_change_dir", lambda: None)

    result = FilterModeService.apply([existing, missing])

    assert result == [existing.resolve()]


def test_wdir_bootstrap_service_builds_chain_with_lang_from_repo():
    fake_wdir = _FakeWdir()
    ctx = SimpleNamespace(
        wdir=fake_wdir,
        wdir_builded=False,
        target_list=[Path("a"), Path("a")],
        param=SimpleNamespace(filter=False),
        config=SimpleNamespace(curses_mode=True),
        lang="",
        repo=SimpleNamespace(data=SimpleNamespace(lang="py")),
    )
    service = WdirBootstrapService()

    built = service.build(cast(Any, ctx), cast(Any, FilterModeService()))

    assert built is fake_wdir
    assert ctx.wdir_builded is True
    assert ctx.target_list == [Path("a")]
    assert ("set_curses", True) in fake_wdir.calls
    assert ("set_lang", "py") in fake_wdir.calls


def test_wdir_bootstrap_service_sets_compile_error_on_build_failure():
    fake_wdir = _FailingWdir()
    ctx = SimpleNamespace(
        wdir=fake_wdir,
        wdir_builded=False,
        target_list=[Path("a")],
        param=SimpleNamespace(filter=False),
        config=SimpleNamespace(curses_mode=False),
        lang="",
        repo=None,
    )
    service = WdirBootstrapService()

    service.build(cast(Any, ctx), cast(Any, FilterModeService()))

    assert fake_wdir.get_solver().exec.error == "x"


def test_opener_factory_configures_language_from_solver():
    settings = SimpleNamespace(app=SimpleNamespace(editor="code"))
    ctx = SimpleNamespace(
        settings=settings,
        target_list=[Path("solver.py")],
        wdir=SimpleNamespace(get_solver=lambda: _FakeSolver([Path("solver.ts")])),
    )

    opener = OpenerFactory.create_for_wdir(cast(Any, ctx))

    assert isinstance(opener, Opener)
    assert opener.language == "ts"
