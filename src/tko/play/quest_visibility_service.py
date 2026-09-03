from __future__ import annotations

from tko.game.game import Game
from tko.game.quest import Quest
from tko.game.task import Task


class QuestVisibilityService:
    @staticmethod
    def is_reachable(quest: Quest) -> bool:
        return True

    @staticmethod
    def is_task_reachable(game: Game, task: Task) -> bool:
        quest = game.quests.get(task.quest_key)
        return quest is not None

    @staticmethod
    def is_quest_closed_in_inbox(quest: Quest) -> bool:
        return False
