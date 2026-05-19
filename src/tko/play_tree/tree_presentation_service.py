from tko.game.game import Game
from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.play.quest_visibility_service import QuestVisibilityService
from tko.play_tree.tree_state import TreeState
from tko.util.rt import RT


class TreePresentationService:
    def build_items(self, game: Game, state: TreeState) -> list[IsTreeItem]:
        items: list[IsTreeItem] = []
        for quest in game.quests.values():
            if not quest.ui.visible:
                continue
            for req in quest.requirements.required_by_ptr:
                if req.basic.full_key == state.selected:
                    quest.ui.is_requirement_color = "y" if QuestVisibilityService.is_reachable(req) else "r"
                    break
            items.append(quest)
            color = "g" if QuestVisibilityService.is_reachable(quest) else "y"
            tasks: list[Task] = [task for task in quest.get_tasks() if task.ui.visible]
            has_hidden = len(tasks) != len(quest.get_tasks())
            if quest.basic.full_key not in state.expanded:
                quest.ui.ligature = RT("┅┄", color) if has_hidden else RT("━─", color)
                continue
            quest.ui.ligature = RT("┅┅", color) if has_hidden else RT("━━", color)
            for task in tasks:
                items.append(task)
        return items