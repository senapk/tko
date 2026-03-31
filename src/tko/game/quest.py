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
        self.set_key(key)
        self.set_title(title)
        self.line_number: int = 0
        self.line: str = ""
        self.__tasks: list[Task] = []
        self.requires: list[str] = []  # 
        self.requires_ptr: list[Quest] = []
        self.required_by_ptr: list[Quest] = []
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

    def get_full_title(self, show_skills: bool) -> Text:
        output = Text().addf("c", self.remote_name).add(":").add(self.get_title())
        if show_skills:
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

    def is_complete(self):
        value = self.get_percent_main()
        return value is None or value >= self.min_percent_completion

    def add_task(self, task: Task):
        task.skills.update(self.skills)  # apply quest skills to task
        self.__tasks.append(task)

    def get_tasks(self):
        return self.__tasks

    def sort_tasks_by_title(self):
        self.__tasks = sorted(self.__tasks, key=lambda t: t.get_title())

    def get_xp(self, include_main: bool, include_side: bool) -> tuple[float, float]:
        """
        Returns a tuple of (earned_xp, total_xp)
        """
        tasks_info: list[QuestGrader.Elem] = []
        for t in self.__tasks:
            if t.task_path == Task.TaskPath.MAIN and not include_main:
                continue
            if t.task_path == Task.TaskPath.SIDE and not include_side:
                continue
            percent = (t.get_rate_percent() * t.get_quality_percent()) / 100.0
            tasks_info.append(QuestGrader.Elem(t.is_optional(), t.xp, percent))
        return QuestGrader.calc_xp_earned_total(tasks_info)
    
    def get_completion(self) -> tuple[int, int]:
        total = 0
        done = 0
        for t in self.__tasks:
            if t.visible:
                total += 1
            if t.is_complete():
                done += 1
        return done, total

    def get_percent(self, include_main: bool, include_side: bool) -> float | None:
        obtained, total = self.get_xp(include_main=include_main, include_side=include_side)
        return QuestGrader.get_percent(obtained, total)

    def get_percent_main(self) -> float | None:
        return self.get_percent(include_main=True, include_side=False)
    
    def get_percent_side(self) -> float | None:
        return self.get_percent(include_main=False, include_side=True)
