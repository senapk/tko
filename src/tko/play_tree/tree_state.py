from tko.game.tree_item import HasTreeIdentity
from typing import Sequence


class TreeFilter:
    def __init__(self, inbox_mode: bool, search_text: str):
        self.inbox_mode: bool = inbox_mode
        self.search_text: str = search_text

    def hide_elements(self) -> bool:
        return self.inbox_mode and self.search_text == ""


class TreeState:
    expanded: set[str] = set()
    selected: str = ""
    selected_index: int = 0
    search: str = ""
    scroll: int = 0

    def ensure_valid_selection(self, items: Sequence[HasTreeIdentity]):
        """Garante que selected sempre aponta para um item visível"""
        if not items:
            self.selected = ""
            self.selected_index = 0
            return

        keys = [i.identity.get_full_key() for i in items]
        if self.selected not in keys:  # fallback_mode
            if self.selected_index < len(keys):
                self.selected = keys[self.selected_index]
            else:
                self.selected = keys[0]

    def get_selected_index(self, items: Sequence[HasTreeIdentity]) -> int:
        if self.selected_index < len(items) and items[self.selected_index].identity.get_full_key() == self.selected:
            return self.selected_index
        for i, item in enumerate(items):
            if item.identity.get_full_key() == self.selected:
                self.selected_index = i
                return i
        return 0

    def get_selected_throw(self, items: Sequence[HasTreeIdentity]) -> HasTreeIdentity:
        for item in items:
            if item.identity.get_full_key() == self.selected:
                return item
        raise IndexError("Selected item not found")

    def move_selection(self, delta: int, items: Sequence[HasTreeIdentity]):
        if not items:
            return

        index = self.get_selected_index(items)
        index += delta
        index = max(0, min(index, len(items) - 1))
        self.selected = items[index].identity.get_full_key()
        self.selected_index = index

    def update_scroll(self, window_height: int, items: Sequence[HasTreeIdentity]):
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
