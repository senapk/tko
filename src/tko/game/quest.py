from __future__ import annotations
from tko.game.task import Task
from tko.util.text import Text
from tko.game.tree_item import TreeItem
from tko.game.quest_grader import QuestGrader

# from typing import override

def startswith(text: str, prefix: str) -> bool: 
    if len(prefix) > len(text):
        return False
    return text[:len(prefix)] == prefix

class Quest(TreeItem):
    def __init__(self, title: str = "", key: str = ""):
        super().__init__()
        self.key: str = key
        self.title: str = title
        self.line_number: int = 0
        self.line: str = ""
        self.__tasks: list[Task] = []
        self.requires: list[str] = []  # 
        self.requires_ptr: list[Quest] = []
        self.prog = False  # progressive tasks, only allow next task if previous is >= 50%
        self.skills: dict[str, int] = {}  # s:{skill} to be applied to all tasks
        self.languages: list[str] = []  # l:language to filter what is showed to user based in default language
        self.qmin: int = 50  # q:{value} 50 percent to complete quest
        self.value: int = 1  # v:{value} quest value in cluster wheighted average
        self.filename = ""
        self.cluster_key = ""
        self.__is_reachable: bool = False

    def get_value(self) -> int:
        return self.value

    def get_full_title(self):
        output = self.title
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

    # @override
    def __str__(self):
        line = str(self.line_number).rjust(3)
        tasks_size = str(len(self.__tasks)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        output = f"{line} {tasks_size} {key}{self.title} {self.skills} {self.requires}"
        return output

    def get_resume_by_percent(self) -> Text:
        value: int = min(100, round(self.get_percent()))
        return Text().addf(self.get_grade_color(), (str(value) + "%").rjust(4))
    
    def get_requirement(self) -> Text:
        return Text().addf("y", f"[{self.qmin}%]")

    def get_grade_color(self) -> str:
        if self.not_started():
            return "m"
        if not self.is_complete():
            return "r"
        if self.get_percent() == 100:
            return "g"
        return "y"

    def is_complete(self):
        return self.get_percent() >= self.qmin

    def add_task(self, task: Task):
        task.skills.update(self.skills)  # apply quest skills to task
        self.__tasks.append(task)

    def get_tasks(self):
        return self.__tasks

    def get_xp(self) -> tuple[float, float]:
        """
        Returns a tuple of (earned_xp, total_xp)
        """
        tasks_info: list[QuestGrader.Elem] = []
        for t in self.__tasks:
            tasks_info.append(QuestGrader.Elem(t.opt, t.xp, t.get_percent()))
        return QuestGrader.calc_xp_earned_total(tasks_info)
        
    def get_percent(self) -> float:
        obtained, total = self.get_xp()
        return QuestGrader.get_percent(obtained, total)

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
