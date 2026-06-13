from __future__ import annotations
from tko.collect.quest_game_data import QuestGameData
from tko.i18n import Msg
from tko.collect.task_user_data import TaskUserData
from typing import Any
from tko.util.console import Console


_COLLECTED_NO_RESUME_DATA = Msg(
    pt="No resume data found in the JSON.",
    en="No resume data found in the JSON.",
)

class Collected:
    class Key:
        quests_str: str = "quests"
        resume_str: str = "resume"
        graph_str: str = "graph"
        history_str: str = "history"
        log_str: str = "log"

    def __init__(self):
        self.task_resume: dict[str, TaskUserData] = {}
        self.task_history: list[TaskUserData] = []
        self.daily_graph: str = ""
        self.full_log: list[str] = []
        self.game_structure: list[QuestGameData] = []

    def load_from_dict(self, json_data: dict[str, Any]):
        if not Collected.Key.resume_str in json_data:
            Console.print(f"{_COLLECTED_NO_RESUME_DATA}")
            return self

        task_resume = json_data.get(Collected.Key.resume_str, None)
        if task_resume is not None:
            for key, value in task_resume.items():
                collected_resume = TaskUserData()
                collected_resume.from_kv(value)
                self.task_resume[key] = collected_resume
        task_history = json_data.get(Collected.Key.history_str, None)
        if task_history is not None:
            for item in task_history:
                collected_history = TaskUserData()
                collected_history.from_kv(item)
                self.task_history.append(collected_history)

        self.daily_graph = json_data.get(Collected.Key.graph_str, self.daily_graph)
        self.full_log = json_data.get(Collected.Key.log_str, self.full_log)
        quest_data = json_data.get(Collected.Key.quests_str, [])
        for quest in quest_data:
            game_quest = QuestGameData(quest.get(QuestGameData.Key.KEY, ""))
            game_quest.load_from_dict(quest)
            self.game_structure.append(game_quest)
        return self

    def get_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        resume_dict: dict[str, Any] = {}
        for key, value in self.task_resume.items():
            resume_dict[key] = value.get_kv(include_key=True, include_quest=True)
            
        output[self.Key.history_str] = [item.get_kv(include_key=True, include_quest=True) for item in self.task_history]
        output[self.Key.resume_str] = resume_dict
        output[self.Key.graph_str] = self.daily_graph
        output[self.Key.log_str] = self.full_log
        output[self.Key.quests_str] = [quest.to_dict() for quest in self.game_structure]
        return output
