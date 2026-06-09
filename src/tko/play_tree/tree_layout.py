from tko.game.game import Game
from tko.config.flags import Flags
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.quest_formatter import QuestFormatter
from typing import Callable


class TreeLayout:
    def __init__(self, task_formatter: TaskFormatter, quest_formatter: QuestFormatter, game: Game, flags: Flags):
        self.task_formatter = task_formatter
        self.quest_formatter = quest_formatter
        self.game = game
        self.flags = flags
        self.get_tree_size_fn: Callable[[], int] | None = None

        self.key_size_min = 20
        self.sentence_cut_min_size = 30

        self.fixed_task_itens_size = 10
        self.use_full_key: bool = False

        self.__key_size: int | None = None

    def reset(self):
        self.__key_size = None

    @property
    def key_size(self) -> int:
        # if self.__key_size is None:
        self.__calculate()
        if self.__key_size is None:
            return self.key_size_min
        return self.__key_size
    
    @property
    def sentence_cut_size(self) -> int:
        if self.get_tree_size_fn is None:
            return 100
        size = self.get_tree_size_fn() - self.fixed_task_itens_size
        if self.flags.show_time.is_true():
            size -= 7
        return size
        
    def __calculate(self):
        game = self.game
        key_sizes: list[int] = []

        for q in game.quests.values():
            for t in q.get_tasks():
                key = t.basic.full_key if self.use_full_key else t.basic.key
                key_sizes.append(len(key))
        self.__key_size = max(key_sizes) if key_sizes else self.key_size_min
