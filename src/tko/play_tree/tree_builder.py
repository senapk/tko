from tko.game.game import Game
from tko.game.task import Task
from tko.game.task_config import TaskMain
from tko.game.tree_item import IsTreeItem
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.tree_state import TreeState, TreeFilter
from tko.play.quest_visibility_service import QuestVisibilityService
from tko.util.rtext import RText
from tko.util.to_asc import SearchAsc


class TreeBuilder:
    def __init__(self, task_formatter: TaskFormatter):
        self.task_formatter = task_formatter
        self.repo = task_formatter.repo

    def filter_by_search(self, game: Game, search_text: str) -> tuple[set[str], str | None]:
        matches: set[str] = set()
        first: str | None = None
        search = SearchAsc(search_text)

        for quest in game.quests.values():
            if search.inside(quest.basic.title):
                first = first or quest.basic.full_key
                matches.add(quest.basic.full_key)

            for task in quest.get_tasks():
                full, _key, _title = self.task_formatter.get_task_full_title(task, None)
                if search.inside(full):
                    first = first or task.basic.full_key
                    matches.add(quest.basic.full_key)
                    matches.add(task.basic.full_key)

        return matches, first

    def select_inbox_enabled(self, game: Game, tf: TreeFilter, task_formatter: TaskFormatter) -> set[str]:
        max_count = 10
        enabled: set[str] = set()
        for q in game.quests.values():
            if QuestVisibilityService.is_quest_closed_in_inbox(q):
                continue
            enabled.add(q.basic.full_key)
            count = 0
            tasks = sorted(
                q.get_tasks(),
                key=lambda t: (t.grader.get_rate_percent() != 100, t.config.path != TaskMain.MAIN)
            )
            for t in tasks:
                if t.grader.get_rate_percent() == 100 and t.grader.get_quality_percent() == 100:
                    continue
                if task_formatter.is_downloaded_for_lang(t):
                    enabled.add(t.basic.full_key)
                    count += 1
                elif count < max_count:
                    enabled.add(t.basic.full_key)
                    count += 1
        return enabled

    def enable_all(self, game: Game) -> set[str]:
        matches: set[str] = set()
        for q in game.quests.values():
            matches.add(q.basic.full_key)
            for t in q.get_tasks():
                matches.add(t.basic.full_key)
        return matches

    def get_enabled_by_mode(self, game: Game, state: TreeState, tfilter: TreeFilter):
        game.update_reachable_and_available()
        if state.search != "":
            enabled, first_match = self.filter_by_search(game, tfilter.search_text)
            if first_match and state.selected == "":
                state.selected = first_match
        elif tfilter.inbox_mode:
            enabled = self.select_inbox_enabled(game, tfilter, self.task_formatter)
        else:
            enabled = self.enable_all(game)
        return enabled
    
    def set_visible(self, game: Game, enabled: set[str]):
        for q in game.quests.values():
            q.ui.is_requirement_color = ""
            if q.basic.full_key in enabled:
                q.ui.visible = True
            else:
                q.ui.visible = False
            for t in q.get_tasks():
                if t.basic.full_key in enabled:
                    t.ui.visible = True
                else:
                    t.ui.visible = False

    def build(self, game: Game, state: TreeState, tfilter: TreeFilter) -> list[IsTreeItem]:
        enabled = self.get_enabled_by_mode(game, state, tfilter)
        self.set_visible(game, enabled)
        items = self.set_colors_and_ligatures(game, state)
        return items
    
    def set_colors_and_ligatures(self, game: Game, state: TreeState) -> list[IsTreeItem]:
        items: list[IsTreeItem] = []
        for q in game.quests.values():
            if not q.ui.visible:
                continue
            for req in q.requirements.required_by_ptr:
                if req.basic.full_key == state.selected:
                    q.ui.is_requirement_color = "y" if QuestVisibilityService.is_reachable(req) else "r"
                    break
            items.append(q)
            color = "g" if QuestVisibilityService.is_reachable(q) else "y"
            tasks: list[Task] = [t for t in q.get_tasks() if t.ui.visible]
            has_hidden = len(tasks) != len(q.get_tasks())
            if q.basic.full_key not in state.expanded:
                q.ui.ligature = RText("┅┄", color) if has_hidden else RText("━─", color)
                continue
            q.ui.ligature = RText("┅┅", color) if has_hidden else RText("━━", color)
            for t in tasks:
                items.append(t)
        return items
