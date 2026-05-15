from tko.game.quest import Quest
from tko.game.task import Task
from tko.play.quest_visibility_service import QuestVisibilityService
from tko.play_tree.task_tree import TaskTree


class SearchService:
    def __init__(self, tree: TaskTree):
        self.tree = tree
        self.game = tree.game
        self.repo = tree.repo
        self.filter_policy = tree.filter_policy

    def update_selected_from_search(self) -> None:
        _, first = self.filter_policy.filter_by_search(self.game, self.tree.state.search)
        self.tree.state.selected = first if first is not None else ""

    def get_selected_safe(self):
        try:
            return self.tree.get_selected_throw()
        except IndexError:
            return None

    def finish(self, selected_key: str, inbox_in_beginning: bool) -> bool:
        item = self.get_selected_safe()
        if item is None:
            return False

        if inbox_in_beginning:
            self.tree.update(force_view_all=False)
            reachable = True
            if isinstance(item, Task):
                reachable = QuestVisibilityService.is_task_reachable(self.game, item)
            elif isinstance(item, Quest):
                reachable = QuestVisibilityService.is_reachable(item)
            if not reachable:
                self.repo.flags.task_view_mode.set_view_all()
            else:
                self.repo.flags.task_view_mode.set_view_inbox()

        self.tree.update()
        self.tree.state.selected = selected_key
        self.tree.state.expanded = set()

        unit = self.get_selected_safe()
        if unit is None:
            return True

        if isinstance(unit, Task):
            self.tree.state.expanded = {unit.basic.remote_name, unit.quest_key}
        elif isinstance(unit, Quest):
            self.tree.state.expanded = {unit.basic.full_key, unit.basic.remote_name}
        return True