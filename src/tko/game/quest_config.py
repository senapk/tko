from __future__ import annotations


class QuestConfig:
    def __init__(self):
        # Percentual minimo para considerar quest completa.
        self.min_percent_completion: int = 50
        self.skills: dict[str, int] = {}
        self.languages: list[str] = []
