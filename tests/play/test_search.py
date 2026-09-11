from types import SimpleNamespace
from typing import Any, cast

from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.play.search import Search
from tko.play.search_service import SearchService


class _DummyFlags:
    class _TaskViewMode:
        def is_inbox(self) -> bool:
            return False

        def set_view_all(self):
            return None

        def set_view_inbox(self):
            return None

    def __init__(self):
        self.task_view_mode = self._TaskViewMode()


class _FilterPolicyNone:
    def filter_by_search(self, _game: Any, _text: str) -> tuple[set[str], str | None]:
        return set(), None


class _FilterPolicyFirst:
    def __init__(self, first: str):
        self.first = first

    def filter_by_search(self, _game: Any, _text: str) -> tuple[set[str], str | None]:
        return {self.first}, self.first


class _DummyTree:
    def __init__(self):
        self.game = SimpleNamespace()
        self.repo = SimpleNamespace(flags=_DummyFlags())
        self.settings = SimpleNamespace()
        self.state = SimpleNamespace(expanded=set(), selected="repo@q1@t1", search="abc")
        self.filter_policy: Any = _FilterPolicyNone()
        self.update_calls = 0
        self.expand_calls = 0

    def get_selected_throw(self) -> IsTreeItem:
        raise IndexError("Selected item not found")

    def update(self, force_view_all: bool = False):
        if force_view_all:
            self.update_calls += 1
        return None

    def expand_all(self):
        self.expand_calls += 1
        return None


class _SearchResultTree(_DummyTree):
    """Small tree model that falls back when a task's quest is collapsed."""

    def __init__(self) -> None:
        super().__init__()
        self.task = Task()
        self.task.basic.source_name = "repo"
        self.task.basic.key = "task"
        self.task.quest_key = "repo@quest"
        self.state.selected = self.task.basic.full_key

    def get_selected_throw(self) -> Task:
        if self.state.selected != self.task.basic.full_key:
            raise IndexError("Selected item not found")
        return self.task

    def get_selected_index(self) -> int:
        return 2

    def update(self, force_view_all: bool = False) -> None:
        self.update_calls += 1
        if self.task.quest_key not in self.state.expanded:
            self.state.selected = "repo@first"


def test_finish_search_does_not_raise_when_selected_item_disappears():
    tree = _DummyTree()
    search = Search(tree=cast(Any, tree))
    search.search_mode = True

    # Must not raise; this used to crash the TUI loop when selection became stale.
    search.finish_search()

    assert search.search_mode is False
    assert tree.state.search == ""


def test_update_index_uses_filter_policy_first_match():
    tree = _DummyTree()
    tree.filter_policy = _FilterPolicyFirst("repo@q1@t2")
    search = Search(tree=cast(Any, tree))

    search.update_index()

    assert tree.state.selected == "repo@q1@t2"


def test_toggle_search_starts_session_and_forces_expanded_view():
    tree = _DummyTree()
    search = Search(tree=cast(Any, tree))

    search.toggle_search()

    assert search.search_mode is True
    assert tree.update_calls == 1
    assert tree.expand_calls == 1


def test_finish_search_expands_selected_task_quest_and_keeps_cursor():
    tree = _SearchResultTree()
    service = SearchService(cast(Any, tree))

    completed = service.finish(tree.task.basic.full_key, inbox_in_beginning=False)

    assert completed is True
    assert tree.state.expanded == {"repo", "repo@quest"}
    assert tree.state.selected == tree.task.basic.full_key
    assert tree.state.selected_index == 2
