from tko.play.flags import Flag, Flags, FlagsMan
from tko.play.floating import Floating, FloatingInput, FloatingInputData
from tko.play.floating_manager import FloatingManager
from tko.play.border import Border
from tko.settings.settings import Settings
from tko.util.text import Text
from tko.play.border import Border
from typing import List, Tuple, Union, Callable
from tko.play.functors import FlagFunctor
from tko.settings.repository import Repository, languages_avaliable


class LanguageSetter:
    def __init__(self, rep: Repository, flagsman: FlagsMan, fman: FloatingManager):
        self.flagsman = flagsman
        self.fman = fman
        self.rep = rep


    def set_language(self):
        options: List[FloatingInputData] = []
        for lang in languages_avaliable:
            options.append(FloatingInputData(TextFunctor(lang), SetLangFunctor(self.rep, self.fman, lang)))

        self.fman.add_input(
            FloatingInput("^")
            .set_header(" Escolha a extensão default para os rascunhos ")
            .set_options(options)
            .set_default_index(languages_avaliable.index(self.rep.get_lang()))
            .set_footer(" Pressione Enter para confirmar ")
        )

class TextFunctor:
    def __init__(self, data: str):
        self.value = data
    
    def __call__(self):
        return Text(self.value)

class SetLangFunctor:
    def __init__(self, rep: Repository, fman: FloatingManager, lang: str):
        self.rep = rep
        self.fman = fman
        self.value = lang

    def __call__(self):
        self.rep.set_lang(self.value.strip())
        self.rep.save_data_to_config_file()
        self.fman.add_input(
            Floating()
            .put_text("")
            .put_text("Linguagem alterada para " + self.value)
            .put_text("")
            .warning()
        )