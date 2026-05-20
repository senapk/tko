from tko.game.game import Game
from tko.game.task_config import TaskMain
from tko.play.quest_visibility_service import QuestVisibilityService
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.tree_state import TreeFilter, TreeState
from tko.util.to_asc import SearchAsc


class TreeFilterPolicy:
    def __init__(self, task_formatter: TaskFormatter):
        self.task_formatter = task_formatter

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

    def select_inbox_enabled(self, game: Game) -> set[str]:
        max_count = 10
        enabled: set[str] = set()
        for quest in game.quests.values():
            if QuestVisibilityService.is_quest_closed_in_inbox(quest):
                continue
            enabled.add(quest.basic.full_key)
            count = 0
            tasks = sorted(
                quest.get_tasks(),
                key=lambda task: (task.grader.get_rate_percent() != 100, task.config.main != TaskMain.MAIN),
            )
            for task in tasks:
                if task.grader.get_rate_percent() == 100 and task.grader.get_quality_percent() == 100:
                    continue
                if self.task_formatter.is_downloaded_for_lang(task):
                    enabled.add(task.basic.full_key)
                    count += 1
                elif count < max_count:
                    enabled.add(task.basic.full_key)
                    count += 1
        return enabled

    @staticmethod
    def enable_all(game: Game) -> set[str]:
        matches: set[str] = set()
        for quest in game.quests.values():
            matches.add(quest.basic.full_key)
            for task in quest.get_tasks():
                matches.add(task.basic.full_key)
        return matches

    def get_enabled_by_mode(self, game: Game, state: TreeState, tree_filter: TreeFilter) -> set[str]:
        game.update_reachable_and_available()
        if tree_filter.is_searching:
            enabled, first_match = self.filter_by_search(game, tree_filter.search_text)
            if first_match and state.selected == "":
                state.selected = first_match
            return enabled
        if tree_filter.should_use_inbox_filter:
            return self.select_inbox_enabled(game)
        return self.enable_all(game)