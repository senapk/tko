from __future__ import annotations
import sys # type: ignore
from tko.collect.task_game_data import TaskGameData
from tko.repository.repository import Repository
from tko.logger.logger import Logger
from tko.collect.task_user_data import TaskUserData
from tko.logger.log_sort import LogSort
from tko.play.daily_graph import DailyGraph
from tko.collect.quest_game_data import QuestGameData

class CollectActions:
    @staticmethod
    def resume(repo: Repository) -> dict[str, TaskUserData]:
        """
        Collect resume data from the repository's logger and return a dictionary mapping task keys to TaskResume objects.
        """
        logger: Logger = repo.logger
        tasks: dict[str, LogSort] = logger.tasks.task_dict
        resume_dict: dict[str, TaskUserData] = {}

        game = repo.game
        quest_map: dict[str, str] = {}
        for quest in game.quests.values():
            for task in quest.get_tasks():
                quest_map[task.basic.full_key] = quest.basic.full_key
        for key, log_sort in tasks.items():
            resume = TaskUserData().setup(log_sort, repo.game.get_task(key))
            resume_dict[key] = resume
        return resume_dict

    @staticmethod
    def daily_graph(rep: Repository, width: int, height: int, colored: bool) -> str:
        dg = DailyGraph(rep.logger, width, height)
        header, image = dg.get_graph()
        if not colored:
            return "\n".join([x.plain() for x in header + image])
        return "\n".join([str(x) for x in image])

    @staticmethod
    def load_game_as_quest_list(rep: Repository) -> list[QuestGameData]:
        game = rep.game
        if not game:
            return []
        output: list[QuestGameData] = []

        for quest in game.quests.values():
            output_quest = QuestGameData(quest.basic.full_key)
            output.append(output_quest)
            for task in quest.get_tasks():
                output_quest.tasks.append(TaskGameData(key=task.basic.full_key, value=task.game.xp, is_leet=task.config.is_eval_test))
        return output
    
