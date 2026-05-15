from dataclasses import dataclass
from typing import Any, cast

import pytest

from tko.play_tree.tree_presentation_service import TreePresentationService
from tko.play_tree.tree_state import TreeState


@dataclass
class Basic:
    full_key: str


class Ui:
    def __init__(self):
        self.visible = False
        self.is_requirement_color = ""
        self.ligature = ""


class Requirement:
    def __init__(self, key: str):
        self.basic = Basic(full_key=key)


class Task:
    def __init__(self, key: str, visible: bool):
        self.basic = Basic(full_key=key)
        self.ui = Ui()
        self.ui.visible = visible


class Quest:
    def __init__(self, key: str, tasks: list[Task], visible: bool = True):
        self.basic = Basic(full_key=key)
        self.ui = Ui()
        self.ui.visible = visible
        self._tasks = tasks
        self.requirements = type("ReqWrap", (), {"required_by_ptr": []})()

    def get_tasks(self) -> list[Task]:
        return self._tasks


class Game:
    def __init__(self, quests: dict[str, Quest]):
        self.quests = quests


def _always_reachable(_quest: Any) -> bool:
    return True


def test_build_items_respects_visibility_and_collapsed_quest(monkeypatch: pytest.MonkeyPatch):
    task1 = Task("repo@q1@t1", visible=True)
    task2 = Task("repo@q1@t2", visible=False)
    quest = Quest("repo@q1", [task1, task2], visible=True)
    game = Game({"repo@q1": quest})
    state = TreeState()
    state.selected = ""
    state.expanded = set()

    monkeypatch.setattr("tko.play_tree.tree_presentation_service.QuestVisibilityService.is_reachable", _always_reachable)

    items = TreePresentationService().build_items(cast(Any, game), state)

    assert [item.basic.full_key for item in items] == ["repo@q1"]


def test_build_items_adds_visible_tasks_when_expanded(monkeypatch: pytest.MonkeyPatch):
    task1 = Task("repo@q1@t1", visible=True)
    task2 = Task("repo@q1@t2", visible=True)
    quest = Quest("repo@q1", [task1, task2], visible=True)
    game = Game({"repo@q1": quest})
    state = TreeState()
    state.selected = ""
    state.expanded = {"repo@q1"}

    monkeypatch.setattr("tko.play_tree.tree_presentation_service.QuestVisibilityService.is_reachable", _always_reachable)

    items = TreePresentationService().build_items(cast(Any, game), state)

    assert [item.basic.full_key for item in items] == ["repo@q1", "repo@q1@t1", "repo@q1@t2"]
