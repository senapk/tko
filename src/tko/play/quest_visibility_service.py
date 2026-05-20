from __future__ import annotations

from tko.game.game import Game
from tko.game.quest import Quest
from tko.game.task import Task


class QuestVisibilityService:
    @staticmethod
    def is_reachable(quest: Quest) -> bool:
        return quest.state.is_reachable

    @staticmethod
    def is_task_reachable(game: Game, task: Task) -> bool:
        quest = game.quests.get(task.quest_key)
        if quest is None:
            return False
        return QuestVisibilityService.is_reachable(quest)

    @staticmethod
    def is_quest_closed_in_inbox(quest: Quest) -> bool:
        percent_all = quest.progress.get_percent()
        return (not QuestVisibilityService.is_reachable(quest)) or percent_all >= 100
