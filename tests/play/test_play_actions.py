from types import SimpleNamespace
from typing import Any, cast

from tko.floating.floating import Floating, FloatingType
from tko.play.play_actions import PlayActions


class _DummyFloatingManager:
    def __init__(self) -> None:
        self.items: list[Floating] = []

    def add_floating(self, item: Floating) -> None:
        self.items.append(item)


class _DummyTree:
    def __init__(self) -> None:
        self.recalculate_calls = 0

    def recalculate_layout(self) -> None:
        self.recalculate_calls += 1


def test_reload_reports_missing_task_as_floating(monkeypatch: Any) -> None:
    class _BrokenGameCoordinator:
        def __init__(self, _repo: object) -> None:
            pass

        def load_game(self) -> None:
            raise FileNotFoundError("t_broken")

    fman = _DummyFloatingManager()
    tree = _DummyTree()
    gui = SimpleNamespace(
        app=SimpleNamespace(),
        settings=SimpleNamespace(),
        fman=fman,
        repo=SimpleNamespace(),
        tree=tree,
        game=SimpleNamespace(),
    )

    monkeypatch.setattr("tko.repository.game_coordinator.GameCoordinator", _BrokenGameCoordinator)

    actions = PlayActions(cast(Any, gui))
    actions.reload()

    assert tree.recalculate_calls == 0
    assert len(fman.items) == 1
    assert fman.items[0].type == FloatingType.ERROR
    assert "t_broken" in "\n".join(line.plain() for line in fman.items[0].content)
