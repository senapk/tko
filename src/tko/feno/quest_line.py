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

    def _calc_ref_sum(self) -> int:
        return sum(l.tm.xp for l in self.lines if isinstance(l, TaskLine) and l.tm.is_ref)

    def render_line(self):
        qf = QuestMatcher(self.qp.quest)
        quest = self.qp.quest
        fields = qf.get_filled_fields()
        ref_sum = self._calc_ref_sum()
        if ref_sum > 0:
            for i, f in enumerate(fields):
                if f.startswith(QuestMatcher.GOAL):
                    fields[i] = f"{QuestMatcher.GOAL}{self._calc_ref_sum()}"

        return f"## {quest.basic.title} <!-- {" ".join(fields)} -->"