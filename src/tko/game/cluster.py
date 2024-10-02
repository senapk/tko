from typing import List, Optional
from .quest import Quest
from ..util.text import Text
from tko.game.tree_item import TreeItem

class Cluster(TreeItem):
    def __init__(self, line_number: int = 0, title: str = "", key: str = "", color: Optional[str] = None):
        super().__init__()
        self.line_number = line_number
        self.quests: List[Quest] = []
        self.color: Optional[str] = color
        self.__is_reachable = False
        self.key = key
        self.title = title

    def is_reachable(self):
        return self.__is_reachable
    
    def set_reachable(self, value: bool):
        self.__is_reachable = value
        return self

    def __str__(self):
        line = str(self.line_number).rjust(3)
        quests_size = str(len(self.quests)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        return f"{line} {quests_size} {key}{self.title}"
    
    def get_grade_color(self) -> str:
        perc = self.get_percent()
        if perc == 0:
            return "m"
        if perc < 50:
            return "r"
        if perc < 100:
            return "y"
        return "g"

    def get_percent(self):
        total = 0
        for q in self.quests:
            total += q.get_percent()
        return total // len(self.quests)

    def get_resume_by_percent(self) -> Text:
        return Text().addf(self.get_grade_color(), f"{self.get_percent()}%".rjust(4))

    def get_resume_by_quests(self):
        total = len(self.quests)
        count = len([q for q in self.quests if q.is_complete()])
        return Text().addf(self.get_grade_color(), f"({count}/{total})")
        
