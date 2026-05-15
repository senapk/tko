from tko.game.tree_item import IsTreeItem
from typing import Sequence


class TreeFilter:
    def __init__(self, inbox_mode: bool, search_text: str):
        self.inbox_mode: bool = inbox_mode
        self.search_text: str = search_text

    def hide_elements(self) -> bool:
        return self.inbox_mode and self.search_text == ""


class TreeState:
    def __init__(self):
        self.expanded: set[str] = set()
        self.selected: str = ""
        self.selected_index: int = 0
        self.search: str = ""
        self.scroll: int = 0

    def ensure_valid_selection(self, items: Sequence[IsTreeItem]):
        """Garante que selected sempre aponta para um item visível"""
        if not items:
            self.selected = ""
            self.selected_index = 0
            return

        keys = [i.basic.full_key for i in items]
        if self.selected not in keys:  # fallback_mode
            if self.selected_index < len(keys):
                self.selected = keys[self.selected_index]
            else:
                self.selected = keys[0]

    def get_selected_index(self, items: Sequence[IsTreeItem]) -> int:
        if self.selected_index < len(items) and items[self.selected_index].basic.full_key == self.selected:
            return self.selected_index
        for i, item in enumerate(items):
            if item.basic.full_key == self.selected:
                self.selected_index = i
                return i
        return 0

    def get_selected_throw(self, items: Sequence[IsTreeItem]) -> IsTreeItem:
        for item in items:
            if item.basic.full_key == self.selected:
                return item
        raise IndexError("Selected item not found")

    def move_selection(self, delta: int, items: Sequence[IsTreeItem]):
        if not items:
            return

        index = self.get_selected_index(items)
        index += delta
        index = max(0, min(index, len(items) - 1))
        self.selected = items[index].basic.full_key
        self.selected_index = index

    def update_scroll(self, window_height: int, items: Sequence[IsTreeItem]):
        """Controla o scroll da tela"""
        if not items:
            self.scroll = 0
            return

        index = self.get_selected_index(items)

        if len(items) <= window_height:
            self.scroll = 0
            return

        if index < self.scroll:
            self.scroll = index
        elif index >= self.scroll + window_height:
            self.scroll = index - window_height + 1
