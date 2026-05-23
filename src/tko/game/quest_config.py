from __future__ import annotations


class QuestConfig:
    DEFAULT_MIN = 50
    def __init__(self):
        # Percentual minimo para considerar quest completa.
        self._threshold: int = self.DEFAULT_MIN
        self.goal_xp: int = 0
        self.skills: set[str] = set()
        self.factor: float = 1.0
        self.languages: set[str] = set()
        self.active: bool = True

    @property
    def threshold(self) -> int:
        return self._threshold
    
    @threshold.setter
    def threshold(self, value: int):
        if value < 0 or value > 100:
            raise ValueError(f"Valor de threshold fora do intervalo (0-100): {value}")
        self._threshold = value
