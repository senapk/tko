from tko.game.quest import Quest
from tko.util.get_md_link import get_md_link
from pathlib import Path

"""
## Quest Title [@key] [+skill[:value]]... [!@quest_required]... [=lang] [=lang] [%min_percent_complete]
Values can be hided with <!-- comment -->
"""

class QuestParser:
    def __init__(self, source_alias: str):
        self.source_alias = source_alias
        self.quest = Quest().set_remote_name(source_alias)
        self.line: str = ""
        self.line_num = 0
        self.filename: Path = Path("")

    def finish_quest(self) -> Quest:
        if self.quest.get_key() == "":
            self.quest.set_key(get_md_link(self.quest.get_title()))
        return self.quest

    def match_full_pattern(self) -> bool:
        if self.line.startswith("## "):
            line = self.line[3:]
        elif self.line.startswith("### "):
            line = self.line[4:]
        else:
            return False

        line = line.replace("<!--", " ").replace("-->", " ").replace("`", " ")
        title = self.process_words(line)
        self.quest.set_title(title)
        return True

    def process_words(self, line: str) -> str:
        words = [tag.strip() for tag in line.split(" ") if tag != ""]

        keys = [tag for tag in words if tag[0] == "@"]
        if keys:
            self.quest.set_key(keys[0])

        # skills
        skills = [t[1:] for t in words if t[0] == "+"]
        if len(skills) > 0:
            self.quest.skills = {}
            for s in skills:
                try:
                    k, v = s.split(":")
                    self.quest.skills[k] = int(v)
                except ValueError:
                    self.quest.skills[s] = 1  # default value is 1 if not specified

        # languages
        languages = [t[1:] for t in words if t[0] == "="]
        if len(languages) > 0:
            self.quest.languages = []
            for l in languages:
                self.quest.languages.append(l)

        # quest percent
        qmin = [t[1:] for t in words if t[0] == "%"]
        if len(qmin) > 0:
            try:
                self.quest.min_percent_completion = int(qmin[0])
            except ValueError:
                self.quest.min_percent_completion = 50
        
        required = [t[1:] for t in words if t[0] == "!"]
        for req_key in required:
            self.quest.add_require_key(req_key)

        words = [w for w in words if w[0] not in ["@", "%", "=", "+", "!"]]
        return " ".join(words)

    def parse_quest(self, filename: Path, line: str, line_num: int) -> None | Quest:
        self.line = line
        self.line_num = line_num
        self.filename: Path = filename
        self.quest.line = self.line
        self.quest.line_number = self.line_num
        self.quest.remote_name = ""

        if self.match_full_pattern():
            return self.finish_quest()

        return None