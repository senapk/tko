from __future__ import annotations
from tko.collect.quest_game_data import QuestGameData
from tko.i18n import Msg, t
from tko.collect.task_user_data import TaskUserData
from typing import Any


_COLLECTED_NO_RESUME_DATA = Msg(
    pt="No resume data found in the JSON.",
    en="No resume data found in the JSON.",
)

class Collected:
    quests_str: str = "quests"
    resume_str: str = "resume"
    graph_str: str = "graph"
    log_str: str = "log"

    def __init__(self):
        self.task_resume: dict[str, TaskUserData] = {}
        self.daily_graph: str = ""
        self.full_log: list[str] = []
        self.game_structure: list[QuestGameData] = []

    def load_from_dict(self, json_data: dict[str, Any]):
        if not Collected.resume_str in json_data:
            print(t(_COLLECTED_NO_RESUME_DATA))
            return self

        task_resume = json_data.get(Collected.resume_str, self.task_resume)
        for key, value in task_resume.items():
            collected_resume = TaskUserData(key, "")
            collected_resume.from_dict(value)
            self.task_resume[key] = collected_resume
        self.daily_graph = json_data.get(Collected.graph_str, self.daily_graph)
        self.full_log = json_data.get(Collected.log_str, self.full_log)
        quest_data = json_data.get(Collected.quests_str, [])
        for quest in quest_data:
            game_quest = QuestGameData(quest.get(QuestGameData.key_str, ""))
            game_quest.load_from_dict(quest)
            self.game_structure.append(game_quest)
        return self

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        resume_dict: dict[str, Any] = {}
        for key, value in self.task_resume.items():
            resume_dict[key] = value.to_dict()
        output[Collected.resume_str] = resume_dict
        output[Collected.graph_str] = self.daily_graph
        output[Collected.log_str] = self.full_log
        output[Collected.quests_str] = [quest.to_dict() for quest in self.game_structure]
        return output
