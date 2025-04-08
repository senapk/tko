from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from tko.game.task import Task
from tko.util.text import Text
from tko.util.get_md_link import get_md_link
from tko.game.tree_item import TreeItem
from tko.play.flags import Flags
import re

class Quest(TreeItem):
    def __init__(self, title: str = "", key: str = ""):
        super().__init__()
        self.key = key
        self.title = title
        self.line_number = 0
        self.line = ""
        self.__tasks: List[Task] = []
        self.skills: Dict[str, int] = {}  # s:skill
        self.requires: List[str] = []  # r:quest_key
        self.languages: List[str] = []  # l:language
        self.requires_ptr: List[Quest] = []
        self.opt = False  # opt
        self.prog = False  # progressive tasks
        self.qmin: Optional[int] = None  # q:  minimo de 50 porcento da pontuação total para completar
        self.tmin: Optional[int] = None  # t: ou ter no mínimo esse valor de todas as tarefas
        self.filename = ""
        self.cluster_key = ""
        self.__is_reachable: bool = False

    def get_full_title(self):
        output = self.title
        if Flags.minimum:
            output += " " + self.get_requirement().get_text()
        if Flags.reward:
            xp = ""
            for s, v in self.skills.items():
                xp += f" +{s}:{v}"
            output += xp
        return output


    def is_reachable(self)-> bool:
        return self.__is_reachable

    def set_reachable(self, value: bool):
        self.__is_reachable = value
        return self
    
    def update_tasks_reachable(self):
        if not self.prog:
            for t in self.__tasks:
                t.set_reachable(True)
            return
        reach = True
        for i in range(len(self.__tasks)):
            if i == 0:
                self.__tasks[i].set_reachable(True)
            else:
                if self.__tasks[i-1].get_percent() < 50:
                    reach = False
                self.__tasks[i].set_reachable(reach)

    def __str__(self):
        line = str(self.line_number).rjust(3)
        tasks_size = str(len(self.__tasks)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        output = f"{line} {tasks_size} {key}{self.title} {self.skills} {self.requires}"
        return output

    def get_resume_by_percent(self) -> Text:
        value = self.get_percent()
        return Text().addf(self.get_grade_color(), (str(value) + "%").rjust(4))
    
    def get_requirement(self) -> Text:
        if self.qmin is not None:
            return Text().addf("y", f"[{self.qmin}%]")
        if self.tmin is not None:
            return Text().addf("y", f"[t>{self.tmin - 1}]")
        return Text()

    def get_resume_by_tasks(self) -> Text:
        tmin = self.tmin if self.tmin is not None else 70
        total = len([t for t in self.__tasks if not t.opt])
        plus = len([t for t in self.__tasks if t.opt])
        count = len([t for t in self.__tasks if t.get_percent() >= tmin])
        output = f"{count}/{total}"
        if plus > 0:
            output += f"+{plus}"
        return Text().addf(self.get_grade_color(), "(" + output + ")")

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
                if not t.opt and t.get_percent() < self.tmin:
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
            if t.get_percent() > 0:
                obtained += int(t.xp * t.get_ratio())

        return obtained, total
        
    def get_percent(self):
        obtained, total = self.get_xp()
        if total == 0:
            return 0
        return obtained * 10 // total

    def in_progress(self):
        if self.is_complete():
            return False
        for t in self.__tasks:
            if t.get_percent() != 0:
                return True
        return False

    def not_started(self):
        if self.is_complete():
            return False
        if self.in_progress():
            return False
        return True


class QuestParser:
    quest: Quest

    def __init__(self):
        self.quest = Quest()
        self.line = ""
        self.line_num = 0
        self.default_qmin_requirement = 50
        self.default_task_xp = 10
        self.filename = ""

    def finish_quest(self) -> Quest:

        if self.quest.key == "":
            self.quest.key = get_md_link(self.quest.title)

        if len(self.quest.skills) == 0:
            self.quest.skills["xp"] = self.default_task_xp
        
        if self.quest.qmin is None and self.quest.tmin is None:
            self.quest.qmin = self.default_qmin_requirement

        return self.quest

    def match_full_pattern(self) -> bool:
        if not self.line.startswith("### "):
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

    def process_raw_tags(self, raw_tags):
        tags = [tag.strip() for tag in raw_tags.split(" ")]

        # skills
        skills = [t[1:] for t in tags if t.startswith("+")]
        if len(skills) > 0:
            self.quest.skills = {}
            for s in skills:
                k, v = s.split(":")
                self.quest.skills[k] = int(v)

        # languages
        languages = [t[2:] for t in tags if t.startswith("l:")]
        if len(languages) > 0:
            self.quest.languages = []
            for l in languages:
                self.quest.languages.append(l)

        self.quest.opt = "opt" in tags
        self.quest.prog = "prog" in tags

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


    def parse_quest(self, filename, line, line_num) -> Optional[Quest]:
        self.line = line
        self.line_num = line_num
        self.filename = filename

        self.quest.line = self.line
        self.quest.line_number = self.line_num
        self.quest.cluster_key = ""

        if self.match_full_pattern():
            return self.finish_quest()
                
        return None
