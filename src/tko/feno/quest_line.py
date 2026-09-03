from tko.feno.task_line import TaskLine
from tko.game.quest import Quest
from tko.game.quest_matcher import QuestMatcher
from tko.game.quest_parser import QuestParser


from pathlib import Path


class QuestLine:
    def __init__(self):
        self.qp: QuestParser = QuestParser("")
        self.lines: list[TaskLine | str] = []

    def parse(self, index_path: Path, line: str) -> bool:
        quest = self.qp.parse_quest(index_path, line, 0)
        return quest is not None

    @property
    def quest(self) -> Quest:
        return self.qp.quest

    @property
    def key(self) -> str:
        return self.qp.quest.basic.key

    def render_line(self):
        qf = QuestMatcher(self.qp.quest)
        fields = qf.get_filled_fields()
        if fields:
            return f"## {self.qp.quest.basic.title} <!-- {' '.join(fields)} -->"
        return f"## {self.qp.quest.basic.title}"
