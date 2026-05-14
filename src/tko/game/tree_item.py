from __future__ import annotations
from tko.util.rtext import RText
from typing import Protocol


class TreeUi:
    def __init__(self):
        self.ligature: RText = RText(" ")
        self.visible: bool = False
        self.is_requirement_color: str = ""

    def clone(self) -> TreeUi:
        new_ui = TreeUi()
        new_ui.ligature = self.ligature
        new_ui.visible = self.visible
        new_ui.is_requirement_color = self.is_requirement_color
        return new_ui

class TreeBasic:
    def __init__(self):
        self.remote_name: str = ""
        self.title: str = ""
        self.__key: str = ""

    def clone(self) -> TreeBasic:
        new_identity = TreeBasic()
        new_identity.remote_name = self.remote_name
        new_identity.title = self.title
        new_identity.__key = self.__key
        return new_identity

    @property
    def key(self) -> str:
        return self.__key
    
    @property
    def full_key(self) -> str:
        return f"{self.remote_name}@{self.__key}"

    @key.setter
    def key(self, value: str):
        if value.startswith("@"):
            value = value[1:]
        self.__key = value
        return self    

class IsTreeItem(Protocol):
    basic: TreeBasic
    ui: TreeUi