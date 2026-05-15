from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tko.game.quest import Quest


class QuestRequirements:
    def __init__(self):
        self.requires: list[str] = []
        self.requires_ptr: list[Quest] = []
        self.required_by_ptr: list[Quest] = []

    def add_require_key(self, remote_name: str, key: str):
        if key.startswith("@"):
            key = key[1:]
        self.requires.append(remote_name + "@" + key)
