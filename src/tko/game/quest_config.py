from __future__ import annotations


class QuestGame:
    def __init__(self):
        self.goal_xp: int = 0
        self.skill: str | None = None
        self.languages: set[str] = set()
        self.active: bool = True
