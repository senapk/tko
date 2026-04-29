from tko.game.game import Game
from tko.play_tree.tree_state import TreeState
from tko.repository.repository import Repository


class TreeRepository:
    def __init__(self, repo: Repository, game: Game):
        self.repo = repo
        self.game = game

    def load_state(self, state: TreeState):
        state.expanded = set(self.repo.data.expanded)
        state.selected = self.repo.data.selected

    def save_state(self, state: TreeState):
        # salvar expanded (somente quests válidas)
        self.repo.data.expanded = [
            x for x in state.expanded
            if x in self.game.quests.keys()
        ]

        # salvar selecionado
        self.repo.data.selected = state.selected
        self.repo.data.selected_index = state.selected_index
