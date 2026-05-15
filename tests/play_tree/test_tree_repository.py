from types import SimpleNamespace
from typing import Any, cast

from tko.play_tree.tree_repository import TreeRepository
from tko.play_tree.tree_state import TreeState


def make_repo_data(expanded: list[str], selected: str, selected_index: int):
    return SimpleNamespace(expanded=expanded, selected=selected, selected_index=selected_index)


def test_load_state_restores_selected_index_and_selection():
    repo = cast(Any, SimpleNamespace(data=make_repo_data(["repo@q1"], "repo@q2", 7)))
    game = cast(Any, SimpleNamespace(quests={"repo@q1": object(), "repo@q2": object()}))
    state = TreeState()

    TreeRepository(repo, game).load_state(state)

    assert state.expanded == {"repo@q1"}
    assert state.selected == "repo@q2"
    assert state.selected_index == 7


def test_save_state_filters_unknown_quests_and_persists_selection_fields():
    repo = cast(Any, SimpleNamespace(data=make_repo_data([], "", 0)))
    game = cast(Any, SimpleNamespace(quests={"repo@q1": object()}))
    state = TreeState()
    state.expanded = {"repo@q1", "repo@missing"}
    state.selected = "repo@q1"
    state.selected_index = 3

    TreeRepository(repo, game).save_state(state)

    assert repo.data.expanded == ["repo@q1"]
    assert repo.data.selected == "repo@q1"
    assert repo.data.selected_index == 3
