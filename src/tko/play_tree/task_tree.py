from tko.game.tree_item import IsTreeItem
from tko.play_tree.formatter_util import FormatterUtil
from tko.play_tree.tree_builder import TreeBuilder
from tko.play_tree.tree_layout import TreeLayout
from tko.play_tree.tree_navigator import TreeNavigator
from tko.play_tree.tree_renderer import TreeRenderer
from tko.play_tree.tree_repository import TreeRepository
from tko.play_tree.tree_state import TreeState, TreeFilter
from tko.config.settings import Settings
from tko.repository.repository import Repository
from tko.util.rtext import RText
from tko.util.to_asc import SearchAsc


class TaskTree:
    def __init__(self, settings: Settings, repo: Repository):
        self.game = repo.game
        self.repo = repo
        self.settings = settings
        self.state = TreeState()
        self.fmt_util = FormatterUtil(settings, repo)
        self.layout = TreeLayout(self.fmt_util)
        self.builder = TreeBuilder(self.fmt_util)
        self.renderer = TreeRenderer(self.fmt_util, self.layout, settings, repo.flags, self.state)
        self.navigator = TreeNavigator()
        self.repository = TreeRepository(repo, self.game)

        # loading configs
        self.state.expanded = set(self.repo.data.expanded)
        self.state.selected = self.repo.data.selected

        self.items: list[IsTreeItem] = []

    def recalculate_layout(self):
        self.layout.reset

    def save_state(self):
        self.repository.save_state(self.state)

    def filter_by_search(self) -> tuple[set[str], str | None]:
        return self.builder.filter_by_search(self.game, self.state.search)

    def get_selected_throw(self) -> IsTreeItem:
        return self.state.get_selected_throw(self.items)
    
    def get_selected_index(self) -> int:
        return self.state.get_selected_index(self.items)

    def toggle(self):
        self.navigator.toggle(self.state, self.items)

    def move_up(self):
        self.navigator.move_up(self.state, self.items)
    
    def move_down(self):
        self.navigator.move_down(self.state, self.items)

    def move_right(self):
        self.navigator.right(self.state, self.items)

    def move_left(self):
        self.navigator.left(self.state, self.items)

    def get_visible_sentences(self, height: int) -> list[RText]:
        self.state.update_scroll(height, self.items)
        visible_items = self.items[
            self.state.scroll : self.state.scroll + height
        ]
        return self.get_rendered_items(visible_items)
    
    def get_rendered_items(self, items: list[IsTreeItem] | None = None) -> list[RText]:
        if items is None:
            items = self.items
        matcher = SearchAsc(self.state.search)
        return [
            self.renderer.render(item, self.state.selected, matcher)
            for item in items
        ]
    
    def update(self, force_view_all: bool = False):
        tree_filter = TreeFilter(
            inbox_mode=self.repo.flags.task_view_mode.is_inbox() and not force_view_all,
            search_text=self.state.search
        )
        self.items = self.builder.build(self.game, self.state, tree_filter)
        self.state.ensure_valid_selection(self.items)
        self.layout.calculate(self.game, self.repo.flags, self.state.expanded)

    def collapse_all(self):
        self.state.expanded.clear()

    def expand_all(self):
        for q in self.game.quests.values():
            self.state.expanded.add(q.basic.full_key)
