from tko.game.game import Game
from tko.play_tree.tree_repository import TreeRepository
from tko.play_tree.tree_state import TreeState


class TreeStateService:
    def __init__(self, state: TreeState, repository: TreeRepository, game: Game):
        self.state = state
        self.repository = repository
        self.game = game

    def load(self):
        self.repository.load_state(self.state)

    def save(self):
        self.repository.save_state(self.state)

    def collapse_all(self):
        self.state.expanded.clear()

    def expand_all(self):
        for quest in self.game.quests.values():
            self.state.expanded.add(quest.basic.full_key)