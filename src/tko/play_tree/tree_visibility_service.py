from tko.game.game import Game


class TreeVisibilityService:
    def apply(self, game: Game, enabled: set[str]):
        for quest in game.quests.values():
            quest.ui.is_requirement_color = ""
            quest.ui.visible = quest.basic.full_key in enabled
            for task in quest.get_tasks():
                task.ui.visible = task.basic.full_key in enabled