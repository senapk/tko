from types import SimpleNamespace
from typing import Any, cast

from tko.play.search import Search


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

    def get_selected_throw(self):
        raise IndexError("Selected item not found")

    def update(self, force_view_all: bool = False):
        if force_view_all:
            self.update_calls += 1
        return None

    def expand_all(self):
        self.expand_calls += 1
        return None


class _DummyFloatingManager:
    pass


def test_finish_search_does_not_raise_when_selected_item_disappears():
    tree = _DummyTree()
    search = Search(tree=cast(Any, tree), fman=cast(Any, _DummyFloatingManager()))
    search.search_mode = True

    # Must not raise; this used to crash the TUI loop when selection became stale.
    search.finish_search()

    assert search.search_mode is False
    assert tree.state.search == ""


def test_update_index_uses_filter_policy_first_match():
    tree = _DummyTree()
    tree.filter_policy = _FilterPolicyFirst("repo@q1@t2")
    search = Search(tree=cast(Any, tree), fman=cast(Any, _DummyFloatingManager()))

    search.update_index()

    assert tree.state.selected == "repo@q1@t2"


def test_toggle_search_starts_session_and_forces_expanded_view():
    tree = _DummyTree()
    search = Search(tree=cast(Any, tree), fman=cast(Any, _DummyFloatingManager()))

    search.toggle_search()

    assert search.search_mode is True
    assert tree.update_calls == 1
    assert tree.expand_calls == 1
