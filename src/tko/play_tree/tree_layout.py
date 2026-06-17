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
        self.insert_quest_keys: bool = False

        self.__quests_key_size: int | None = None
        self.__task_key_size: int | None = None

    def reset(self):
        self.__quests_key_size = None
        self.__task_key_size = None

    @property
    def quest_key_pad(self) -> int:
        if self.__quests_key_size is None:
            self.__calculate()
        if self.__quests_key_size is None:
            return self.key_size_min
        return self.__quests_key_size

    @property
    def task_key_pad(self) -> int:
        if self.__task_key_size is None:
            self.__calculate()
        if self.__task_key_size is None:
            return self.key_size_min
        return self.__task_key_size
    
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
        tasks_key_sizes: list[int] = []
        quests_key_sizes: list[int] = []

        for q in game.quests.values():
            quests_key_sizes.append(len(q.basic.key))
            for t in q.get_tasks():
                key = t.basic.full_key if self.use_full_key else t.basic.key
                tasks_key_sizes.append(len(key))
        self.__task_key_size = max(tasks_key_sizes) if tasks_key_sizes else self.key_size_min
        self.__quests_key_size = max(quests_key_sizes) if quests_key_sizes else self.key_size_min
