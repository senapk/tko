from .tasktree import TaskTree
from ..game.task import Task
from ..game.quest import Quest
from ..game.game import Game
from .flags import Flag, Flags, FlagsMan
from .floating import Floating
from .floating_manager import FloatingManager
from tko.play.border import Border
from tko.settings.settings import Settings
from tko.util.sentence import Sentence
from .border import Border
from typing import List, Tuple, Union, Callable
from .functors import FlagFunctor
from tko.settings.rep_settings import RepData, languages_avaliable

def empty_fn():
    pass

class ConfigItem:
    def __init__(self, flag: Flag, fn: Callable[[], None], sentence: Sentence = Sentence() ):
        self.flag = flag
        self.fn: Callable[[], None] = fn
        self.sentence = sentence


class Config:
    def __init__(self, rep: RepData, flagsman: FlagsMan, fman: FloatingManager, settings: Settings):
        self.index: int = 0
        self.flagsman = flagsman
        self.style = Border(settings.app)
        self.gen_graph: bool = False
        self.app = settings.app
        self.colors = settings.colors
        self.fman = fman
        self.rep = rep
        self.enabled = False
        self.size = len(self.get_elements())

    def enable(self):
        self.enabled = True
    
    def disable(self):
        self.enabled = False

    def activate_selected(self):
        elements = self.get_elements()
        chosen = elements[self.index]
        chosen.fn()

    def move_down(self):
        self.index += 1
        if self.index == self.size:
            self.index = 0

    def move_up(self):
        self.index -= 1
        if self.index == -1:
            self.index = self.size - 1

    def mark_focused(self, index, elem: Flag) -> Sentence:
        pad = 14 if index == self.index else 14
        sentence = self.style.get_flag_sentence(elem, pad)

        if index == self.index and self.enabled:
            focus = self.colors.focused_item
            return sentence
        return Sentence("    ").add(sentence)

    def graph_toggle(self):
        self.gen_graph = not self.gen_graph

    def get_elements(self) -> List[ConfigItem]:
        elements: List[ConfigItem] = []
        for flag in self.flagsman.left:
            item = ConfigItem(flag, FlagFunctor(flag))
            elements.append(item)
        border_values = ["1" if self.app.has_borders() else "0"]
        graph_values = ["1" if self.gen_graph else "0"]
        bordas = Flag().set_name("Bordas").set_keycode("B").set_values(border_values).set_description("Ativa as bordas se a fonte tiver suporte    ").set_bool()
        elements.append(ConfigItem(bordas, self.app.toggle_borders))
        grafo = Flag().set_name("Grafo").set_keycode("G").set_values(graph_values)   .set_description("Ativa a geração do grafo do repositório     ").set_bool()
        elements.append(ConfigItem(grafo, self.graph_toggle))
        language = Flag().set_name("Linguagem").set_values([]).set_keycode("L")      .set_description("Muda a linguagem de download dos rascunhos  ")
        elements.append(ConfigItem(language, lambda: self.set_language(False)))

        if Flags.config.is_true():
            for i in range(len(elements)):
                elements[i].sentence = self.mark_focused(i, elements[i].flag)
        return elements


    # def set_rootdir(self, only_if_empty=True):
    #     if only_if_empty and self.app._rootdir != "":
    #         return

    #     def chama(value):
    #         if value == "yes":
    #             self.app._rootdir = os.path.abspath(os.getcwd())
    #             self.settings.save_settings()
    #             self.fman.add_input(
    #                 Floating()
    #                 .put_text("")
    #                 .put_text("Diretório raiz definido como ")
    #                 .put_text("")
    #                 .put_text("  " + os.getcwd())
    #                 .put_text("")
    #                 .put_text("Você pode também pode alterar")
    #                 .put_text("o diretório raiz navegando para o")
    #                 .put_text("diretório desejado e executando o comando")
    #                 .put_text("")
    #                 .put_text("  tko config --root .")
    #                 .put_text("")
    #                 .warning()
    #             )
    #         else:
    #             self.fman.add_input(
    #                 Floating()
    #                 .put_text("")
    #                 .put_text("Navegue para o diretório desejado e tente novamente.")
    #                 .put_text("")
    #                 .put_text("Você pode também pode alterar")
    #                 .put_text("o diretório raiz navegando para o")
    #                 .put_text("diretório desejado e executando o comando")
    #                 .put_text("")
    #                 .put_text("tko config --root .")
    #                 .put_text("")
    #                 .warning()
    #             )

    #     self.fman.add_input(
    #         Floating()
    #         .put_text("")
    #         .put_text("Você deseja utilizar o diretório")
    #         .put_text("atual como diretório raiz do tko?")
    #         .put_text("")
    #         .put_text(os.getcwd())
    #         .put_text("")
    #         .put_text("como raiz para o repositório de " + self.rep_alias + "?")
    #         .put_text("")
    #         .put_text("Selecione e tecle Enter")
    #         .put_text("")
    #         .set_options(["yes", "no"])
    #         .answer(chama)
    #     )

    def set_language(self, only_if_empty=True):
        if only_if_empty and self.rep.get_lang() != "":
            return

        def back(value):
            self.rep.set_lang(value)
            self.rep.save_data_to_json()
            self.fman.add_input(
                Floating()
                .put_text("")
                .put_text("Linguagem alterada para " + value)
                .put_text("")
                .warning()
            )

        self.fman.add_input(
            Floating()
            .put_text("")
            .put_text("Escolha a extensão default para os rascunhos")
            .put_text("")
            .put_text("Selecione e tecle Enter.")
            .put_text("")
            .set_options(languages_avaliable)
            .answer(back)
        )