from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.tree_item import HasTreeIdentity
from tko.play_tree.tree_state import TreeState


class TreeNavigator:
    def move_up(self, state: TreeState, items: list[HasTreeIdentity]):
        state.move_selection(-1, items)

    def move_down(self, state: TreeState, items: list[HasTreeIdentity]):
        state.move_selection(+1, items)

    def toggle(self, state: TreeState, items: list[HasTreeIdentity]):
        """Expande/contrai se for quest"""
        if not items:
            return

        index = state.get_selected_index(items)
        item = items[index]

        if isinstance(item, Quest):
            key = item.identity.get_full_key()
            if key in state.expanded:
                state.expanded.remove(key)
            else:
                state.expanded.add(key)

    def right(self, state: TreeState, items: list[HasTreeIdentity]):
        if not items:
            return

        index = state.get_selected_index(items)
        item = items[index]

        if isinstance(item, Quest):
            key = item.identity.get_full_key()
            if key not in state.expanded:
                state.expanded.add(key)
                return

            index += 1
            while index < len(items):
                if isinstance(items[index], Quest):
                    state.selected = items[index].identity.get_full_key()
                    return
                index += 1
            return

        if isinstance(item, Task):
            while index < len(items):
                if isinstance(items[index], Quest):
                    state.selected = items[index].identity.get_full_key()
                    return
                index += 1

    def left(self, state: TreeState, items: list[HasTreeIdentity]):
        if not items:
            return

        index = state.get_selected_index(items)
        item = items[index]

        if isinstance(item, Quest):
            key = item.identity.get_full_key()

            if key in state.expanded:
                state.expanded.remove(key)
                return

            index -= 1
            while index >= 0:
                if isinstance(items[index], Quest):
                    state.selected = items[index].identity.get_full_key()
                    return
                index -= 1

        if isinstance(item, Task):
            while index >= 0:
                if isinstance(items[index], Quest):
                    state.selected = items[index].identity.get_full_key()
                    return
                index -= 1
