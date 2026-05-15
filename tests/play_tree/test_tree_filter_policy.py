from dataclasses import dataclass
from typing import Any, cast

import pytest

from tko.play_tree.tree_filter_policy import TreeFilterPolicy
from tko.play_tree.tree_state import TreeFilter, TreeState


@dataclass
class Basic:
    full_key: str
    title: str


class FakeTask:
    def __init__(self, full_key: str, title: str):
        self.basic = Basic(full_key=full_key, title=title)


class FakeQuest:
    def __init__(self, full_key: str, title: str, tasks: list[FakeTask]):
        self.basic = Basic(full_key=full_key, title=title)
        self._tasks = tasks

    def get_tasks(self) -> list[FakeTask]:
        return self._tasks


class FakeGame:
    def __init__(self, quests: dict[str, FakeQuest]):
        self.quests = quests
        self.updated = False

    def update_reachable_and_available(self):
        self.updated = True


class FakeTaskFormatter:
    def get_task_full_title(self, task: FakeTask, key_pad: int | None) -> tuple[str, str, str]:
        return task.basic.title, "", task.basic.title

    def is_downloaded_for_lang(self, task: FakeTask) -> bool:
        return False


def test_filter_by_search_matches_quest_and_task_titles():
    formatter = FakeTaskFormatter()
    policy = TreeFilterPolicy(cast(Any, formatter))
    game = FakeGame(
        {
            "repo@q1": FakeQuest(
                full_key="repo@q1",
                title="Quest One",
                tasks=[FakeTask("repo@q1@t1", "alpha task"), FakeTask("repo@q1@t2", "beta task")],
            )
        }
    )

    enabled, first = policy.filter_by_search(cast(Any, game), "beta")

    assert first == "repo@q1@t2"
    assert enabled == {"repo@q1", "repo@q1@t2"}


def test_get_enabled_by_mode_uses_search_and_sets_first_selected_when_empty():
    formatter = FakeTaskFormatter()
    policy = TreeFilterPolicy(cast(Any, formatter))
    game = FakeGame(
        {
            "repo@q1": FakeQuest(
                full_key="repo@q1",
                title="Quest One",
                tasks=[FakeTask("repo@q1@t1", "alpha task")],
            )
        }
    )
    state = TreeState()

    enabled = policy.get_enabled_by_mode(cast(Any, game), state, TreeFilter(inbox_mode=False, search_text="alpha"))

    assert game.updated is True
    assert enabled == {"repo@q1", "repo@q1@t1"}
    assert state.selected == "repo@q1@t1"


def test_get_enabled_by_mode_uses_inbox_policy_when_requested(monkeypatch: pytest.MonkeyPatch):
    formatter = FakeTaskFormatter()
    policy = TreeFilterPolicy(cast(Any, formatter))
    game = FakeGame({})
    state = TreeState()

    def _fake_inbox_enabled(_game: Any) -> set[str]:
        return {"repo@q2"}

    monkeypatch.setattr(policy, "select_inbox_enabled", _fake_inbox_enabled)

    enabled = policy.get_enabled_by_mode(cast(Any, game), state, TreeFilter(inbox_mode=True, search_text=""))

    assert game.updated is True
    assert enabled == {"repo@q2"}
