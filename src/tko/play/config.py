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
from typing import List, Tuple, Union
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

    def mark_focused(self, index, elem: Union[Flag, Tuple[str, str]]) -> Sentence:
        pad = 14 if index == self.index else 14
        if isinstance(elem, Flag):
            sentence = self.style.get_flag_sentence(elem, pad)
        else:
            sentence = self.style.border_round("M", elem[0].ljust(pad) + elem[1])

        if index == self.index:
            focus = self.colors.focused_item
            return Sentence("") + self.style.border_round(focus, sentence.get_text()[1:-1])
        return Sentence("    ").add(sentence)

    def get_elements(self):
        elements: List[Union[Flag, Tuple[str, str]]] = []
        for flag in self.flagsman.left:            
            elements.append(flag)

        bordas = Flag().set_name("Bordas").set_char("B").set_values(["1" if self.app.has_borders() else "0"]).text("Ativa ou desativa as bordas").bool()
        elements.append(bordas)

        grafo = Flag().set_name("Grafo").set_char("G").set_values(["1" if self.gen_graph else "0"]).text("Ativa a geração do grafo").bool()
        elements.append(grafo)
        destiny = Flag().set_name("DirDestino").set_values([]).set_char("D").text("Muda o diretório root de download")
        elements.append(destiny)
        language = Flag().set_name("Linguagem").set_values([]).set_char("L").text("Muda a linguagem de download dos rascunhos")
        elements.append(language)
        # elements.append(("DirDestino", "[D]"))
        # elements.append(("Linguagem", "[L]"))
        output: List[Sentence] = []
        if Flags.config.is_true():
            for i in range(len(elements)):
                sentence = self.mark_focused(i, elements[i])
                output.append(sentence)

        return output

    