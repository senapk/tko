from __future__ import annotations
from tko.game.task import Task
from tko.util.text import Text
from tko.game.tree_item import TreeItem
from tko.game.quest_grader import QuestGrader
from tko.play.flags import Flags

# from typing import override

def startswith(text: str, prefix: str) -> bool: 
    if len(prefix) > len(text):
        return False
    return text[:len(prefix)] == prefix

class Quest(TreeItem):
    def __init__(self, title: str = "", key: str = ""):
        super().__init__()
        self.set_key(key)
        self.set_title(title)
        self.line_number: int = 0
        self.line: str = ""
        self.__tasks: list[Task] = []
        self.requires: list[str] = []  # 
        self.requires_ptr: list[Quest] = []
        self.skills: dict[str, int] = {}  # s:{skill} to be applied to all tasks
        self.languages: list[str] = []  # l:language to filter what is showed to user based in default language
        self.min_percent_completion: int = 50  # q:{value} 50 percent to complete quest
        self.filename = ""
        self.remote_name = ""
        self.__is_reachable: bool = False

    def add_require_key(self, key: str):
        if key.startswith("@"):
            key = key[1:]
        self.requires.append(self.get_remote_name() + "@" + key)

    def get_full_title(self) -> Text:
        output = Text().add(self.remote_name).add(":").add(self.get_title())
        if Flags.show_panel.get_value() == "1" and Flags.panel.get_value() == Flags.panel_skills:
            for skill, value in self.skills.items():
                if value > 1:
                    output.addf('b', f" +{skill}*{value}")
                else:
                    output.addf('b', f" +{skill}")
        return output

    def is_reachable(self)-> bool:
        return self.__is_reachable

    def set_reachable(self, value: bool):
        self.__is_reachable = value
        return self
    
    def update_tasks_reachable(self):
        for t in self.__tasks:
            t.set_reachable(True)
        return

    # @override
    def __str__(self):
        line = str(self.line_number).rjust(3)
        tasks_size = str(len(self.__tasks)).rjust(2, "0")
        key = "" if self.get_full_key() == self.get_title() else self.get_full_key() + " "
        output = f"{line} {tasks_size} {key}{self.get_title()} {self.skills} {self.requires}"
        return output

    def get_resume_by_percent(self) -> Text:
        value: int = min(100, round(self.get_percent()))
        return Text().addf(self.get_grade_color(), (str(value) + "%").rjust(4))
    
    def get_requirement(self) -> Text:
        return Text().addf("y", f"[{self.min_percent_completion}%]")

    def get_grade_color(self) -> str:
        if self.not_started():
            return "m"
        if not self.is_complete():
            return "r"
        if self.get_percent() == 100:
            return "g"
        return "y"

    def is_complete(self):
        return self.get_percent() >= self.min_percent_completion

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
            tasks_info.append(QuestGrader.Elem(t.is_optional(), t.xp, t.get_percent()))
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
