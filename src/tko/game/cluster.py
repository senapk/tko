from tko.game.quest import Quest
from tko.util.text import Text
from tko.game.tree_item import TreeItem
# from typing import override

class Cluster(TreeItem):
    def __init__(self, line_number: int = 0, title: str = "", key: str = "", color: None | str = None):
        super().__init__()
        self.line_number = line_number
        self.__quests: list[Quest] = []
        self.color: None | str = color
        self.__is_reachable = False
        self.key = key
        self.title = title
        self.main_cluster: bool = False  # if this is the main cluster, used to count skills and levels

    def add_quest(self, quest: Quest):
        self.__quests.append(quest)
        return self

    def remove_empty_or_other_language(self, language: str):
        # self.__quests = [q for q in self.__quests if len(q.get_tasks()) > 0]
        quests: list[Quest] = []
        for q in self.__quests:
            if len(q.get_tasks()) == 0:
                continue
            if len(q.languages) == 0 or language in q.languages:
                quests.append(q)
        self.__quests = quests

        return self

    def get_quests(self) -> list[Quest]:
        return self.__quests

    def is_reachable(self):
        return self.__is_reachable
    
    def set_reachable(self, value: bool):
        self.__is_reachable = value
        return self

    # @override
    def __str__(self):
        line = str(self.line_number).rjust(3)
        quests_size = str(len(self.__quests)).rjust(2, "0")
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

    def get_percent(self) -> float:
        total = 0
        weighted_total = 0
        for q in self.__quests:
            total += q.get_percent() * q.get_value()
            weighted_total += q.get_value()
        if weighted_total == 0:
            return 0.0
        return total / weighted_total

    def get_resume_by_percent(self) -> Text:
        return Text().addf(self.get_grade_color(), f"{round(self.get_percent())}%".rjust(4))

    def get_resume_by_quests(self):
        total = len(self.__quests)
        count = len([q for q in self.__quests if q.is_complete()])
        return Text().addf(self.get_grade_color(), f"({count}/{total})")
        
