from tko.game.tree_item import IsTreeItem
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.time_formatter import TimeFormatter
from tko.play_tree.quest_formatter import QuestFormatter
from tko.play_tree.tree_builder import TreeBuilder
from tko.play_tree.tree_filter_policy import TreeFilterPolicy
from tko.play_tree.tree_layout import TreeLayout
from tko.play_tree.tree_presentation_service import TreePresentationService
from tko.play_tree.tree_renderer import TreeRenderer
from tko.play_tree.tree_repository import TreeRepository
from tko.play_tree.tree_selection_service import TreeSelectionService
from tko.play_tree.tree_state_service import TreeStateService
from tko.play_tree.tree_state import TreeState, TreeFilter
from tko.play_tree.tree_visibility_service import TreeVisibilityService
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
        self.task_formatter = TaskFormatter(settings, repo)
        self.time_formatter = TimeFormatter(repo)
        self.quest_formatter = QuestFormatter(settings, self.time_formatter)
        self.filter_policy = TreeFilterPolicy(self.task_formatter)
        self.visibility_service = TreeVisibilityService()
        self.presentation_service = TreePresentationService()
        self.layout = TreeLayout(self.task_formatter, self.quest_formatter)
        self.builder = TreeBuilder(self.filter_policy, self.visibility_service, self.presentation_service)
        self.renderer = TreeRenderer(
            self.task_formatter,
            self.quest_formatter,
            self.time_formatter,
            self.layout,
            settings,
            repo.flags,
            self.state,
        )
        self.selection = TreeSelectionService(self.state)
        self.repository = TreeRepository(repo, self.game)
        self.state_service = TreeStateService(self.state, self.repository, self.game)
        self.state_service.load()

        self.items: list[IsTreeItem] = []

    def recalculate_layout(self):
        self.layout.reset

    def save_state(self):
        self.state_service.save()

    def get_selected_throw(self) -> IsTreeItem:
        return self.selection.get_selected_throw(self.items)
    
    def get_selected_index(self) -> int:
        return self.selection.get_selected_index(self.items)

    def toggle(self):
        self.selection.toggle(self.items)

    def move_up(self):
        self.selection.move_up(self.items)
    
    def move_down(self):
        self.selection.move_down(self.items)

    def move_right(self):
        self.selection.move_right(self.items)

    def move_left(self):
        self.selection.move_left(self.items)

    def get_visible_sentences(self, height: int) -> list[tuple[RText, IsTreeItem]]:
        self.selection.update_scroll(height, self.items)
        visible_items = self.items[
            self.state.scroll : self.state.scroll + height
        ]
        return self.get_rendered_items(visible_items)
    
    def get_rendered_items(self, items: list[IsTreeItem] | None = None) -> list[tuple[RText, IsTreeItem]]:
        if items is None:
            items = self.items
        matcher = SearchAsc(self.state.search)
        return [
            (self.renderer.render(item, self.state.selected, matcher), item)
            for item in items
        ]
    
    def update(self, force_view_all: bool = False):
        tree_filter = TreeFilter(
            inbox_mode=self.repo.flags.task_view_mode.is_inbox() and not force_view_all,
            search_text=self.state.search
        )
        self.selection.ensure_valid_selection(self.items)
        self.layout.calculate(self.game, self.repo.flags, self.state.expanded)
        self.items = self.builder.build(self.game, self.state, tree_filter)

    def collapse_all(self):
        self.state_service.collapse_all()

    def expand_all(self):
        self.state_service.expand_all()
