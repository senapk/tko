from tko.game.game import Game
from tko.game.task import Task
from tko.game.task_config import TaskMain
from tko.game.tree_item import TreeItem
from tko.play_tree.formatter_util import FormatterUtil
from tko.play_tree.tree_state import TreeState, TreeFilter
from tko.util.rtext import RText
from tko.util.to_asc import SearchAsc


class TreeBuilder:
    def __init__(self, fmt_util: FormatterUtil):
        self.fmt_util = fmt_util
        self.repo = fmt_util.repo

    def filter_by_search(self, game: Game, search_text: str) -> tuple[set[str], str | None]:
        matches: set[str] = set()
        first: str | None = None
        search = SearchAsc(search_text)

        for quest in game.quests.values():
            if search.inside(quest.get_title()):
                first = first or quest.get_full_key()
                matches.add(quest.get_full_key())

            for task in quest.get_tasks():
                full, _key, _title = task.get_full_title(None)
                if search.inside(full):
                    first = first or task.get_full_key()
                    matches.add(quest.get_full_key())
                    matches.add(task.get_full_key())

        return matches, first

    def select_inbox_enabled(self, game: Game, tf: TreeFilter, fmt_util: FormatterUtil) -> set[str]:
        max_count = 10
        enabled: set[str] = set()
        for q in game.quests.values():
            _, pall = q.get_percent_main_and_all()
            if not q.is_reachable() or pall >= 100:
                continue
            enabled.add(q.get_full_key())
            count = 0
            tasks = sorted(
                q.get_tasks(),
                key=lambda t: (t.get_rate_percent() != 100, t.config.path != TaskMain.MAIN)
            )
            for t in tasks:
                if t.get_rate_percent() == 100 and t.get_quality_percent() == 100:
                    continue
                if fmt_util.is_downloaded_for_lang(t):
                    enabled.add(t.get_full_key())
                    count += 1
                elif count < max_count:
                    enabled.add(t.get_full_key())
                    count += 1
        return enabled

    def enable_all(self, game: Game) -> set[str]:
        matches: set[str] = set()
        for q in game.quests.values():
            matches.add(q.get_full_key())
            for t in q.get_tasks():
                matches.add(t.get_full_key())
        return matches

    def get_enabled_by_mode(self, game: Game, state: TreeState, tfilter: TreeFilter):
        game.update_reachable_and_available()
        if state.search != "":
            enabled, first_match = self.filter_by_search(game, tfilter.search_text)
            if first_match and state.selected == "":
                state.selected = first_match
        elif self.repo.flags.task_view_mode.is_inbox():
            enabled = self.select_inbox_enabled(game, tfilter, self.fmt_util)
        else:
            enabled = self.enable_all(game)
        return enabled
    
    def set_visible(self, game: Game, enabled: set[str]):
        for q in game.quests.values():
            q.is_requirement_color = ""
            if q.get_full_key() in enabled:
                q.visible = True
            else:
                q.visible = False
            for t in q.get_tasks():
                if t.get_full_key() in enabled:
                    t.visible = True
                else:
                    t.visible = False

    def build(self, game: Game, state: TreeState, tfilter: TreeFilter) -> list[TreeItem]:
        enabled = self.get_enabled_by_mode(game, state, tfilter)
        self.set_visible(game, enabled)
        items = self.set_colors_and_ligatures(game, state)
        return items
    
    def set_colors_and_ligatures(self, game: Game, state: TreeState) -> list[TreeItem]:
        items: list[TreeItem] = []
        for q in game.quests.values():
            if not q.visible:
                continue
            for req in q.required_by_ptr:
                if req.get_full_key() == state.selected:
                    q.is_requirement_color = "y" if req.is_reachable() else "r"
                    break
            items.append(q)
            color = "g" if q.is_reachable() else "y"
            tasks: list[Task] = [t for t in q.get_tasks() if t.visible]
            has_hidden = len(tasks) != len(q.get_tasks())
            if q.get_full_key() not in state.expanded:
                q.ligature = RText("┅┄", color) if has_hidden else RText("━─", color)
                continue
            q.ligature = RText("┅┅", color) if has_hidden else RText("━━", color)
            for t in tasks:
                items.append(t)
        return items
