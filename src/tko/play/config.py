from tko.play.flags import Flag, Flags, FlagsMan
from tko.play.floating import Floating
from tko.play.floating_manager import FloatingManager
from tko.play.border import Border
from tko.settings.settings import Settings
from tko.util.sentence import Sentence
from tko.play.border import Border
from typing import List, Tuple, Union, Callable
from tko.play.functors import FlagFunctor
from tko.settings.rep_settings import RepData, languages_avaliable

def empty_fn():
    pass

class ConfigItem:
    def __init__(self, flag: Flag, fn: Callable[[], None], sentence: Sentence = Sentence() ):
        self.flag = flag
        self.fn: Callable[[], None] = fn
        self.sentence = sentence


class Config:
    def __init__(self, settings: Settings, rep: RepData, flagsman: FlagsMan, fman: FloatingManager):
        self.index: int = 0
        self.flagsman = flagsman
        self.border = Border(settings.app)
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
        sentence = self.border.get_flag_sentence(elem, pad)

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
        images_values = ["1" if self.app.has_images() else "0"]
        bordas = Flag().set_name("Bordas").set_keycode("B").set_values(border_values).set_description("Ativa as bordas se a fonte tiver suporte    ").set_bool()
        elements.append(ConfigItem(bordas, self.app.toggle_borders))
        grafo = Flag().set_name("Grafo").set_keycode("G").set_values(graph_values)   .set_description("Ativa a geração do grafo do repositório     ").set_bool()
        elements.append(ConfigItem(grafo, self.graph_toggle))
        images = Flag().set_name("Imagens").set_keycode("I").set_values(images_values)    .set_description("Mostra imagens de abertura e sucesso        ").location("left")
        elements.append(ConfigItem(images, self.app.toggle_images))
       
        language = Flag().set_name("Linguagem").set_values([]).set_keycode("L")      .set_description("Muda a linguagem de download dos rascunhos  ")
        elements.append(ConfigItem(language, lambda: self.set_language(False)))

        if Flags.config.is_true():
            for i in range(len(elements)):
                elements[i].sentence = self.mark_focused(i, elements[i].flag)
        return elements

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