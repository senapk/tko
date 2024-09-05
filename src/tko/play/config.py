from .tasktree import TaskTree
from ..game.task import Task
from ..game.quest import Quest
from ..game.game import Game
from .flags import Flag, Flags, FlagsMan
from .floating import Floating
from .floating_manager import FloatingManager
import curses
from tko.settings.settings import Settings
from tko.util.sentence import Sentence
from .border import Border
from typing import List
from .functors import FlagFunctor
from .input_manager import InputManager

class Config:
    def __init__(self, flagsman: FlagsMan, fman: FloatingManager, style: Border, settings: Settings):
        self.index: int = 0
        self.flagsman = flagsman
        self.style = style
        self.gen_graph: bool = False
        self.app = settings.app
        self.colors = settings.colors
        self.fman = fman
        self.size = len(self.get_elements())

    def move_down(self):
        self.index += 1
        if self.index == self.size:
            self.index = 0

    def move_up(self):
        self.index -= 1
        if self.index == -1:
            self.index = self.size - 1

    def mark_focused_sentence(self, sentence: Sentence):
        focus = self.colors.focused_item
        for i in range(1, len(sentence.data) - 1):
            if sentence.data[i].text == " ":
                break
            sentence.data[i].fmt = focus

    def get_elements(self):
        elements: List[Sentence] = []
        pad = 11
        for flag in self.flagsman.left:            
            elements.append(self.style.get_flag_sentence(flag, pad))

        bordas = Flag().name("Bordas").char("B").values(["1" if self.app.has_borders() else "0"]).text("Ativa ou desativa as bordas").bool()
        elements.append(self.style.get_flag_sentence(bordas, pad))

        grafo = Flag().name("Grafo").char("G").values(["1" if self.gen_graph else "0"]).text("Ativa a geração do grafo").bool()
        elements.append(self.style.get_flag_sentence(grafo, pad))

        color = "M"
        elements.append(self.style.border_round(color, "DirDestino [D]"))
        elements.append(self.style.border_round(color, "Linguagem  [L]"))

        if Flags.config.is_true():
            for i, value in enumerate(elements):
                if i == self.index:
                    self.mark_focused_sentence(value)

        return elements

    