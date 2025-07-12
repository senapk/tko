from tko.game.quest import Quest, startswith
from tko.util.get_md_link import get_md_link


class QuestParser:
    quest: Quest

    def __init__(self):
        self.quest = Quest()
        self.line: str = ""
        self.line_num = 0
        self.filename: str = ""

    def finish_quest(self) -> Quest:

        if self.quest.key == "":
            self.quest.key = get_md_link(self.quest.title)
        return self.quest

    def match_full_pattern(self) -> bool:
        if not startswith(self.line, "### "):
            return False
        line = self.line[4:]

        pieces: list[str] = line.split("<!--")

        # html tags
        if len(pieces) > 1:
            middle_end: list[str] = pieces[1].split("-->")
            middle: str = middle_end[0]
            end: str = middle_end[1]
            line = pieces[0] + end # removendo raw text
            self.process_raw_tags(middle)

        self.quest.title = line
        if "[](" in line:
            pieces = line.split("[](")
            self.quest.title = pieces[0]

            del pieces[0]
            for p in pieces:
                key = p.split(")")[0]
                if key[0] == "#":
                    key = key[1:]
                self.quest.requires.append(key)

        return True

    def process_raw_tags(self, raw_tags: str):
        tags = [tag.strip() for tag in raw_tags.split(" ")]

        # skills
        skills = [t[1:] for t in tags if t.startswith("+")]
        if len(skills) > 0:
            self.quest.skills = {}
            for s in skills:
                try:
                    k, v = s.split(":")
                    self.quest.skills[k] = int(v)
                except ValueError:
                    self.quest.skills[s] = 1  # default value is 1 if not specified

        # languages
        languages = [t[2:] for t in tags if t.startswith("l:")]
        if len(languages) > 0:
            self.quest.languages = []
            for l in languages:
                self.quest.languages.append(l)
        self.quest.prog = "prog" in tags

        # quest percent
        qmin = [t[2:] for t in tags if t.startswith("q:")]

        # quest percent
        value = [t[2:] for t in tags if t.startswith("v:")]

        if len(value) > 0:
            try:
                self.quest.value = int(value[0])
            except ValueError:
                self.quest.value = 0

        if len(qmin) > 0:
            try:
                self.quest.qmin = int(qmin[0])
            except ValueError:
                self.quest.qmin = 50
            



    def parse_quest(self, filename: str, line: str, line_num: int) -> None | Quest:
        self.line = line
        self.line_num = line_num
        self.filename = filename

        self.quest.line = self.line
        self.quest.line_number = self.line_num
        self.quest.cluster_key = ""

        if self.match_full_pattern():
            return self.finish_quest()

        return None