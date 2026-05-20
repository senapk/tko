from __future__ import annotations


class QuestConfig:
    def __init__(self):
        # Percentual minimo para considerar quest completa.
        self.threshold: int = 50
        self.total_xp: int = 0
        self.skills: dict[str, float] = {}
        self.languages: list[str] = []
        self.active: bool = True
