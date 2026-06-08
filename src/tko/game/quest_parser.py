from loguru import logger

from tko.game.quest_matcher import QuestMatcher
from tko.game.quest import Quest
from tko.util.get_md_link import get_md_link
from pathlib import Path



class QuestParser:
    def __init__(self, source_alias: str):
        self.source_alias = source_alias
        self.quest = Quest()
        self.quest.basic.remote_name = source_alias
        self.raw_line: str = ""
        self.line_num = 0
        self.filename: Path = Path("")

    def finish_quest(self) -> Quest:
        if self.quest.basic.key == "":
            self.quest.basic.key = get_md_link(self.quest.basic.title)
        return self.quest

    def match_full_pattern(self) -> bool:
        if self.raw_line.startswith("## "):
            line = self.raw_line[3:]
        elif self.raw_line.startswith("### "):
            line = self.raw_line[4:]
        else:
            return False

        line = line.replace("<!--", " ").replace("-->", " ").replace("`", " ")
        qt = QuestMatcher(self.quest)
        qt.process_fields(line)
        for w in qt.warnings:
            logger.warning(w)
        self.quest.basic.title = qt.remove_fields_from_title(line)
        return True

    def parse_quest(self, filename: Path, line: str, line_num: int) -> None | Quest:
        self.raw_line = line
        self.line_num = line_num
        self.filename: Path = filename
        self.quest.source.line = self.raw_line
        self.quest.source.line_number = self.line_num
        self.quest.basic.remote_name = ""

        if self.match_full_pattern():
            return self.finish_quest()

        return None