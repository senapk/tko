from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pytest import MonkeyPatch

from tko.config.settings import Settings
from tko.game.task import Task
from tko.run.wdir import Wdir
from tko.tester import tester as tester_module


class FakeTesterApp:
    instances: int = 0
    results: list[Callable[[], bool] | None] = []

    def __init__(self, **_kwargs: object) -> None:
        FakeTesterApp.instances += 1

    def run(self) -> Callable[[], bool] | None:
        return FakeTesterApp.results.pop(0)


def test_interactive_enter_repeats_before_returning_to_tester(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    settings = Settings(tmp_path)
    wdir = Wdir(settings)
    repeat_calls: int = 0

    def free_run() -> bool:
        nonlocal repeat_calls
        repeat_calls += 1
        return repeat_calls == 1

    FakeTesterApp.instances = 0
    FakeTesterApp.results = [free_run, None]
    monkeypatch.setattr("tko.ui_textual.TkoTesterApp", FakeTesterApp)

    tester_module.Tester(settings, None, wdir, Task(), None).run()

    assert repeat_calls == 2
    assert FakeTesterApp.instances == 2
