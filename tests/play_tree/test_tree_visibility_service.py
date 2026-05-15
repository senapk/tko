from dataclasses import dataclass
from typing import Any, cast

from tko.play_tree.tree_visibility_service import TreeVisibilityService


@dataclass
class Basic:
    full_key: str


class Ui:
    def __init__(self):
        self.visible = False
        self.is_requirement_color = "x"


class Task:
    def __init__(self, key: str):
        self.basic = Basic(full_key=key)
        self.ui = Ui()


class Quest:
    def __init__(self, key: str, tasks: list[Task]):
        self.basic = Basic(full_key=key)
        self.ui = Ui()
        self._tasks = tasks

    def get_tasks(self) -> list[Task]:
        return self._tasks


class Game:
    def __init__(self, quests: dict[str, Quest]):
        self.quests = quests


def test_apply_marks_visibility_and_resets_requirement_color():
    task1 = Task("repo@q1@t1")
    task2 = Task("repo@q1@t2")
    quest = Quest("repo@q1", [task1, task2])
    quest.ui.is_requirement_color = "r"
    game = Game({"repo@q1": quest})

    TreeVisibilityService().apply(cast(Any, game), {"repo@q1", "repo@q1@t2"})

    assert quest.ui.visible is True
    assert quest.ui.is_requirement_color == ""
    assert task1.ui.visible is False
    assert task2.ui.visible is True
