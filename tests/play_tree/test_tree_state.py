import pytest

from tko.game.tree_item import TreeItem
from tko.play_tree.tree_state import TreeFilter, TreeState


def make_item(key: str, remote_name: str = "repo") -> TreeItem:
    return TreeItem().set_remote_name(remote_name).set_key(key).set_title(key)


class TestTreeFilter:
    def test_hide_elements_only_in_inbox_without_search(self):
        assert TreeFilter(inbox_mode=True, search_text="").hide_elements() is True
        assert TreeFilter(inbox_mode=True, search_text="graph").hide_elements() is False
        assert TreeFilter(inbox_mode=False, search_text="").hide_elements() is False


class TestTreeState:
    def test_ensure_valid_selection_resets_empty_state_when_no_items(self):
        state = TreeState()
        state.selected = "repo@missing"
        state.selected_index = 3

        state.ensure_valid_selection([])

        assert state.selected == ""
        assert state.selected_index == 0

    def test_ensure_valid_selection_uses_selected_index_or_first_item_as_fallback(self):
        items = [make_item("a"), make_item("b"), make_item("c")]

        state = TreeState()
        state.selected = "repo@missing"
        state.selected_index = 1
        state.ensure_valid_selection(items)
        assert state.selected == "repo@b"

        state.selected = "repo@missing-again"
        state.selected_index = 10
        state.ensure_valid_selection(items)
        assert state.selected == "repo@a"

    def test_get_selected_index_uses_cached_index_and_updates_when_needed(self):
        items = [make_item("a"), make_item("b"), make_item("c")]
        state = TreeState()
        state.selected = "repo@b"
        state.selected_index = 1

        assert state.get_selected_index(items) == 1

        state.selected = "repo@c"
        state.selected_index = 0

        assert state.get_selected_index(items) == 2
        assert state.selected_index == 2

    def test_get_selected_throw_returns_item_or_raises(self):
        items = [make_item("a"), make_item("b")]
        state = TreeState()
        state.selected = "repo@b"

        assert state.get_selected_throw(items).get_full_key() == "repo@b"

        state.selected = "repo@missing"
        with pytest.raises(IndexError, match="Selected item not found"):
            state.get_selected_throw(items)

    def test_move_selection_clamps_to_bounds_and_updates_selection(self):
        items = [make_item("a"), make_item("b"), make_item("c")]
        state = TreeState()
        state.selected = "repo@b"
        state.selected_index = 1

        state.move_selection(1, items)
        assert state.selected == "repo@c"
        assert state.selected_index == 2

        state.move_selection(10, items)
        assert state.selected == "repo@c"
        assert state.selected_index == 2

        state.move_selection(-10, items)
        assert state.selected == "repo@a"
        assert state.selected_index == 0

    def test_update_scroll_resets_or_adjusts_to_keep_selection_visible(self):
        items = [make_item(str(index)) for index in range(6)]
        state = TreeState()

        state.scroll = 4
        state.update_scroll(window_height=3, items=[])
        assert state.scroll == 0

        state.selected = "repo@1"
        state.selected_index = 1
        state.scroll = 3
        state.update_scroll(window_height=10, items=items)
        assert state.scroll == 0

        state.scroll = 3
        state.update_scroll(window_height=3, items=items)
        assert state.scroll == 1

        state.selected = "repo@5"
        state.selected_index = 5
        state.scroll = 1
        state.update_scroll(window_height=3, items=items)
        assert state.scroll == 3