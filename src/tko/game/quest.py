from typing import Dict, List, Optional, Tuple
from .task import Task
from ..util.sentence import Sentence
import re


class Quest:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.title = ""
        self.__tasks: List[Task] = []
        self.skills: Dict[str, int] = {} # s:skill
        self.cluster = ""
        self.requires = [] # r:quest_key
        self.requires_ptr = []
        self.opt = False # opt
        self.qmin: Optional[int] = None # q:  minimo de 50 porcento da pontuação total para completar
        self.tmin: Optional[int] = None  # t: ou ter no mínimo esse valor de todas as tarefas

    def __str__(self):
        line = str(self.line_number).rjust(3)
        tasks_size = str(len(self.__tasks)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        output = f"{line} {tasks_size} {key}{self.title} {self.skills} {self.requires}"
        return output

    def get_resume_by_percent(self) -> Sentence:
        value = self.get_percent()
        return Sentence().addf(self.get_grade_color(), (str(value) + "%"))
    
    def get_requirement(self) -> Sentence:
        if self.qmin is not None:
            return Sentence().addf("y", f"[{self.qmin}%]")
        if self.tmin is not None:
            return Sentence().addf("y", f"[t>{self.tmin - 1}]")
        return Sentence()

    def get_resume_by_tasks(self) -> Sentence:
        tmin = self.tmin if self.tmin is not None else 7
        total = len([t for t in self.__tasks if not t.opt])
        plus = len([t for t in self.__tasks if t.opt])
        count = len([t for t in self.__tasks if t.grade >= tmin])
        output = f"{count}/{total}"
        if plus > 0:
            output += f"+{plus}"
        return Sentence().addf(self.get_grade_color(), "(" + output + ")")

    def get_grade_color(self) -> str:
        if self.not_started():
            return "m"
        if not self.is_complete():
            return "r"
        if self.get_percent() == 100:
            return "g"
        return "y"

    def is_complete(self):
        if self.qmin is not None:
            return self.get_percent() >= self.qmin
        # task complete mode
        if self.tmin is not None:
            for t in self.__tasks:
                if not t.opt and t.grade < self.tmin:
                    return False
        return True

    def add_task(self, task: Task, filename: str):
        if self.qmin is not None:
            if task.opt:
                print(f"Quests com requerimento de porcentagem não deve ter Tasks opcionais")
                print(f"{filename}:{task.line_number} {task.key}")
                exit(1)
        task.qskills = self.skills

        task.xp = 0
        for s in task.skills:
            task.xp += task.skills[s]

        for s in task.qskills:
            task.xp += task.qskills[s]
        
        self.__tasks.append(task)

    def get_tasks(self):
        return self.__tasks

    def get_xp(self) -> Tuple[int, int]:
        total = 0
        obtained = 0
        for t in self.__tasks:
            total += t.xp
            if t.grade > 0:
                obtained += t.xp * t.grade // 10

        return obtained, total
        
    def get_percent(self):
        obtained, total = self.get_xp()
        if total == 0:
            return 0
        return obtained * 100 // total

    def in_progress(self):
        if self.is_complete():
            return False
        for t in self.__tasks:
            if t.grade != 0:
                return True
        return False

    def not_started(self):
        if self.is_complete():
            return False
        if self.in_progress():
            return False
        return True

    def is_reachable(self, cache: Dict[str, bool]):
        if self.key in cache:
            return cache[self.key]

        if len(self.requires_ptr) == 0:
            cache[self.key] = True
            return True
        cache[self.key] = all( [r.is_complete() and r.is_reachable(cache) for r in self.requires_ptr] )
        return cache[self.key]
    
class QuestParser:
    quest: Quest

    def __init__(self):
        self.quest = Quest()
        self.line = ""
        self.line_num = 0
        self.default_qmin_requirement = 50
        self.default_task_xp = 10

    @staticmethod
    def get_md_link(title: str) -> str:
        if title is None:
            return ""
        title = title.lower()
        out = ""
        for c in title:
            if c == " " or c == "-":
                out += "-"
            elif c == "_":
                out += "_"
            elif c.isalnum():
                out += c
        return out

    def finish_quest(self) -> Quest:

        if self.quest.key == "":
            self.quest.key = QuestParser.get_md_link(self.quest.title)

        if len(self.quest.skills) == 0:
            self.quest.skills["xp"] = self.default_task_xp
        
        if self.quest.qmin is None and self.quest.tmin is None:
            self.quest.qmin = self.default_qmin_requirement

        return self.quest

    def match_full_pattern(self):
        fullpattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->.*$"
        match = re.match(fullpattern, self.line)
        tags = []

        if not match:
            return False
        self.quest.title = match.group(1).strip()
        tags_raw = match.group(2).strip()
        tags = [tag.strip() for tag in tags_raw.split()]

        # key
        keys = [t[1:] for t in tags if t.startswith("@")]
        if len(keys) > 0:
            self.quest.key = keys[0]

        # skills
        skills = [t[1:] for t in tags if t.startswith("+")]
        if len(skills) > 0:
            self.quest.skills = {}
            for s in skills:
                k, v = s.split(":")
                self.quest.skills[k] = int(v)
        # requires
        self.quest.requires = [t[2:] for t in tags if t.startswith("r:")]

        self.quest.opt = "opt" in tags
        # type
        # try:
        #     self.quest.type = [t[1:] for t in tags if t.startswith("#")][0]
        # except:
        #     self.quest.type = "main"
        
        # quest percent
        qmin = [t[2:] for t in tags if t.startswith("q:")]
        
        if len(qmin) > 0:
            self.quest.qmin = int(qmin[0])

        # task min value requirement
        tmin = [t[2:] for t in tags if t.startswith("t:")]
        if len(tmin) > 0:
            self.quest.tmin = int(tmin[0])
            if self.quest.tmin > 10:
                print("fail: tmin > 10")
                exit(1)
        return True

    def __match_minimal_pattern(self):
        minipattern = r"^#+\s*(.*?)\s*$"
        match = re.match(minipattern, self.line)
        if match:
            self.quest.title = match.group(1).strip()
            return True
        return False

    def parse_quest(self, filename, line, line_num) -> Optional[Quest]:
        self.line = line
        self.line_num = line_num
        self.filename = filename

        self.quest.line = self.line
        self.quest.line_number = self.line_num
        self.quest.cluster = ""

        if self.match_full_pattern():
            return self.finish_quest()
        
        if self.__match_minimal_pattern():
            return self.finish_quest()
        
        return None
