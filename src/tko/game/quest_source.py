from __future__ import annotations


class QuestSource:
    def __init__(self):
        self.file: str = ""
        self.line_number: int = 0
        self.line: str = ""
