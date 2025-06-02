from tko.play.flags import FlagsMan
from tko.play.floating import Floating, FloatingInput, FloatingInputData
from tko.play.floating_manager import FloatingManager
from tko.settings.languages import available_languages
from tko.util.text import Text
from tko.settings.repository import Repository
from tko.settings.settings import Settings

class LanguageSetter:
    def __init__(self, settings: Settings, rep: Repository, flagsman: FlagsMan, fman: FloatingManager):
        self.flagsman = flagsman
        self.fman = fman
        self.rep = rep
        self.settings = settings


    def set_language(self):
        options: list[FloatingInputData] = []
        for lang in available_languages:
            options.append(FloatingInputData(TextFunctor(lang), SetLangFunctor(self.settings, self.rep, self.fman, lang)))

        self.fman.add_input(
            FloatingInput(self.settings, "^")
            .set_header(" Escolha a extensão default para os rascunhos ")
            .set_options(options)
            .set_default_index(available_languages.index(self.rep.get_lang()))
            .set_footer(" Escolha e reinicie o tko para aplicar!!!!! ")
        )

class TextFunctor:
    def __init__(self, data: str):
        self.value = data
    
    def __call__(self):
        return Text().add(self.value)

class SetLangFunctor:
    def __init__(self, settings: Settings, rep: Repository, fman: FloatingManager, lang: str):
        self.rep = rep
        self.fman = fman
        self.value = lang
        self.settings = settings

    def __call__(self):
        self.rep.set_lang(self.value.strip())
        self.rep.save_config()
        self.fman.add_input(
            Floating(self.settings, "v>")
            .put_text("")
            .put_text("Linguagem alterada para " + self.value)
            .put_text("")
            .warning()
        )
