from tko.game.tree_item import IsTreeItem
from tko.play_tree.tree_navigator import TreeNavigator
from tko.play_tree.tree_state import TreeState


class TreeSelectionService:
    def __init__(self, state: TreeState):
        self.state = state
        self.navigator = TreeNavigator()

    def ensure_valid_selection(self, items: list[IsTreeItem]):
        self.state.ensure_valid_selection(items)

    def update_scroll(self, height: int, items: list[IsTreeItem]):
        self.state.update_scroll(height, items)

    def get_selected_throw(self, items: list[IsTreeItem]) -> IsTreeItem:
        return self.state.get_selected_throw(items)

    def get_selected_index(self, items: list[IsTreeItem]) -> int:
        return self.state.get_selected_index(items)

    def toggle(self, items: list[IsTreeItem]):
        self.navigator.toggle(self.state, items)

    def move_up(self, items: list[IsTreeItem]):
        self.navigator.move_up(self.state, items)

    def move_down(self, items: list[IsTreeItem]):
        self.navigator.move_down(self.state, items)

    def move_right(self, items: list[IsTreeItem]):
        self.navigator.right(self.state, items)

    def move_left(self, items: list[IsTreeItem]):
        self.navigator.left(self.state, items)