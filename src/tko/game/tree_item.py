from __future__ import annotations
from typing import Protocol


class TreeUi:
    def __init__(self):
        self.visible: bool = False

    def clone(self) -> TreeUi:
        new_ui = TreeUi()
        new_ui.visible = self.visible
        return new_ui

class TreeBasic:
    def __init__(self):
        self.source_name: str = ""
        self.title: str = ""
        self.__key: str = ""

    def clone(self) -> TreeBasic:
        new_identity = TreeBasic()
        new_identity.source_name = self.source_name
        new_identity.title = self.title
        new_identity.__key = self.__key
        return new_identity

    @property
    def key(self) -> str:
        return self.__key
    
    @property
    def full_key(self) -> str:
        return f"{self.source_name}@{self.__key}"

    @key.setter
    def key(self, value: str):
        if value.startswith("@"):
            value = value[1:]
        self.__key = value
        return self    

class TreeItem:
    """Estado comum de qualquer item exibido na árvore de atividades."""

    def __init__(self) -> None:
        self.basic = TreeBasic()
        self.ui = TreeUi()

class IsTreeItem(Protocol):
    basic: TreeBasic
    ui: TreeUi
