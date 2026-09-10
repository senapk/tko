from types import SimpleNamespace

from tko.floating.floating_manager import FloatingManager
from tko.play.play import Play
from tko.play_tree.task_tree import TaskTree
from tko.play_tree.tree_state import TreeState


class FakeViewMode:
    def __init__(self, value: str):
        self.value = value

    def is_pinned(self) -> bool:
        return self.value == "pinned"

    def is_inbox(self) -> bool:
        return self.is_pinned()

    def set_view_all(self):
        self.value = "all"

    def set_view_pinned(self):
        self.value = "pinned"


class FakeFilterPolicy:
    def select_pinned_enabled(self, _game, pinned):
        return {key for key in pinned if key.startswith("task:")}


class FakeBuilder:
    def __init__(self):
        self.filters = []

    def build(self, _game, _state, tree_filter):
        self.filters.append(tree_filter)
        return []


class FakeSelection:
    def ensure_valid_selection(self, _items):
        pass


def make_tree(mode: str, pinned: set[str]):
    tree = object.__new__(TaskTree)
    tree.game = object()
    tree.repo = SimpleNamespace(flags=SimpleNamespace(task_view_mode=FakeViewMode(mode)))
    tree.state = TreeState()
    tree.state.pinned = pinned
    tree.filter_policy = FakeFilterPolicy()
    tree.builder = FakeBuilder()
    tree.selection = FakeSelection()
    return tree


def test_empty_pinned_view_falls_back_to_all_tasks():
    tree = make_tree("pinned", set())

    tree.update()

    assert tree.repo.flags.task_view_mode.value == "all"
    assert tree.builder.filters[0].inbox_mode is False


def test_pinned_view_with_task_is_preserved():
    tree = make_tree("pinned", {"task:one"})

    tree.update()

    assert tree.repo.flags.task_view_mode.value == "pinned"
    assert tree.builder.filters[0].inbox_mode is True


def test_switch_to_pinned_keeps_all_view_and_shows_floating_when_empty():
    play = object.__new__(Play)
    play.flags = SimpleNamespace(task_view_mode=FakeViewMode("all"))
    play.tree = make_tree("all", set())
    play.fman = FloatingManager()

    play.switch_to_pinned()

    assert play.flags.task_view_mode.value == "all"
    floating = play.fman.get_top()
    assert floating is not None
    assert [str(line) for line in floating.content] == ["Nenhuma tarefa fixada."]


def test_switch_to_pinned_changes_view_when_a_task_is_pinned():
    play = object.__new__(Play)
    play.flags = SimpleNamespace(task_view_mode=FakeViewMode("all"))
    play.tree = make_tree("all", {"task:one"})
    play.fman = FloatingManager()

    play.switch_to_pinned()

    assert play.flags.task_view_mode.value == "pinned"
    assert play.fman.get_top() is None
