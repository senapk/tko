from tko.game.game import Game
from tko.game.tree_item import IsTreeItem
from tko.play_tree.tree_filter_policy import TreeFilterPolicy
from tko.play_tree.tree_presentation_service import TreePresentationService
from tko.play_tree.tree_visibility_service import TreeVisibilityService
from tko.play_tree.tree_state import TreeState, TreeFilter


class TreeBuilder:
    def __init__(
        self,
        filter_policy: TreeFilterPolicy,
        visibility_service: TreeVisibilityService,
        presentation_service: TreePresentationService,
    ):
        self.filter_policy = filter_policy
        self.visibility_service = visibility_service
        self.presentation_service = presentation_service
    
    def build(self, game: Game, state: TreeState, tfilter: TreeFilter) -> list[IsTreeItem]:
        enabled = self.filter_policy.get_enabled_by_mode(game, state, tfilter)
        self.visibility_service.apply(game, enabled)
        return self.presentation_service.build_items(game, state)
