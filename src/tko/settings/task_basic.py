from __future__ import annotations
# from typing import override

class TaskBasic:
    def __init__(self, key: str = ""):
        self.key = key
        self.coverage = 0
        self.autonomy = 0
        self.skill = 0
        self.timestamp: str = ""

    def set_coverage(self, value: int):
        if value >= 0:
            self.coverage = value
        return self

    def set_approach(self, value: int):
        if value >= 0:
            self.autonomy = value
        return self
    
    def set_autonomy(self, value: int):
        if value >= 0:
            self.skill = value
        return self

    def set_timestamp(self, timestamp: str):
        self.timestamp = timestamp
        return self

    # @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskBasic):
            return False
        return self.coverage == other.coverage and self.autonomy == other.autonomy and self.skill == other.skill

    # @override
    def __str__(self):
        return "{" + f'k:{self.key}, c:{self.coverage}, a:{self.autonomy}, s:{self.skill}' + "}"