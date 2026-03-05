from tko.play.floating_drop_down import FloatingDropDown
from tko.play.flags import FlagsMan
from tko.play.floating import Floating
from tko.play.floating_drop_down import FloatingInputData
from tko.play.floating_manager import FloatingManager
from tko.settings.languages import available_languages
from tko.util.text import Text
from tko.settings.repository import Repository
from tko.settings.settings import Settings


class LanguageSetter:

    @staticmethod
    def check_lang_in_text_mode(repo: Repository):
        lang = repo.data.lang
        if lang == "":
            options = available_languages
            print("\nLinguagem padrão ainda não foi definida.\n")
            while True:
                print("Escolha entre as opções a seguir ", end="")
                print("[" + ", ".join(options) + "]", ":", end=" ")
                lang = input()
                if lang in options:
                    break
            repo.data.lang = lang
            repo.save_config()
            
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
            FloatingDropDown().set_floating(
                Floating()
                .top()
                .set_header(" Escolha a extensão default para os rascunhos ")
                .set_footer(" Escolha e reinicie o tko para aplicar!!!!! ")
                .set_text_ljust()
            )
            .set_options(options)
            .set_default_index(available_languages.index(self.rep.data.get_lang()))
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
        self.rep.data.set_lang(self.value.strip())
        self.rep.save_config()
        self.fman.add_input(
            Floating()
            .bottom()
            .right()
            .put_text("")
            .put_text("Linguagem alterada para " + self.value)
            .put_text("")
            .set_warning()
        )
