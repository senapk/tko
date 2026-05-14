from tko.game.game import Game
from tko.play.flags import Flags
from tko.play_tree.formatter_util import FormatterUtil


class TreeLayout:
    def __init__(self, fmt_util: FormatterUtil):
        self.fmt_util = fmt_util
        self.key_size_min = 20
        self.sentence_cut_min_size = 30
        self.sentence_cut_max_size = 80

        self.fixed_task_itens_size = 12
        self.fixed_quest_itens_size = 10
        
        self.key_size: int = 0
        self.sentence_cut_size: int = 0  # 0 if not calculated yet

    def reset(self):
        self.key_size = 0
        self.sentence_cut_size = 0

    def calculate(self, game: Game, flags: Flags, expanded: set[str]):
        if self.sentence_cut_size != 0:
            return
        key_sizes: list[int] = []
        sentence_cut: list[int] = []

        for q in game.quests.values():
            for t in q.get_tasks():
                key_sizes.append(len(t.basic.key))
        self.key_size = max(key_sizes) if key_sizes else self.key_size_min

        for q in game.quests.values():
            sentence_cut.append(len(q.get_full_title(flags.panel.is_skills())) + self.fixed_quest_itens_size)
            for t in q.get_tasks():
                _full, _, _ = self.fmt_util.get_full_title(t, self.key_size)
                sentence_cut.append(len(_full) + self.fixed_task_itens_size)

        self.sentence_cut_size = max(max(sentence_cut), self.sentence_cut_min_size) if sentence_cut else self.sentence_cut_min_size
        if self.sentence_cut_size > self.sentence_cut_max_size:
            self.sentence_cut_size = self.sentence_cut_max_size
