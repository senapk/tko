from types import SimpleNamespace
from typing import Any, cast

from tko.play.search_session_service import SearchSessionService


class _TaskViewMode:
    def __init__(self, inbox: bool):
        self._inbox = inbox
        self.set_all_calls = 0

    def is_inbox(self) -> bool:
        return self._inbox

    def set_view_all(self) -> None:
        self.set_all_calls += 1


class _DummyTree:
    def __init__(self, inbox: bool):
        self.state = SimpleNamespace(expanded={"repo@q1"}, selected="repo@q1@t1", search="abc")
        self.repo = SimpleNamespace(flags=SimpleNamespace(task_view_mode=_TaskViewMode(inbox)))
        self.update_calls = 0
        self.expand_calls = 0

    def update(self, force_view_all: bool = False):
        if force_view_all:
            self.update_calls += 1

    def expand_all(self):
        self.expand_calls += 1


def test_start_saves_state_and_forces_view_all():
    tree = _DummyTree(inbox=True)
    session = SearchSessionService(cast(Any, tree))

    session.start()

    assert session.backup_expanded == ["repo@q1"]
    assert session.backup_selected == "repo@q1@t1"
    assert session.inbox_in_beggining is True
    assert tree.update_calls == 1
    assert tree.expand_calls == 1
    assert tree.repo.flags.task_view_mode.set_all_calls == 1


def test_cancel_restores_backup_state_and_clears_search_text():
    tree = _DummyTree(inbox=False)
    session = SearchSessionService(cast(Any, tree))
    session.start()

    tree.state.search = "needle"
    tree.state.selected = "repo@q2@t9"
    tree.state.expanded = {"repo@q2"}

    session.cancel()

    assert tree.state.search == ""
    assert tree.state.selected == "repo@q1@t1"
    assert tree.state.expanded == {"repo@q1"}
