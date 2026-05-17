from tko.floating import Floating
from tko.floating.floating_drop_down import FloatingDropDown
from tko.floating.floating_drop_down import FloatingInputData
from tko.floating.floating_manager import FloatingManager
from tko.repository.repository_loader import RepositoryLoader
from tko.util.rtext import RText
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.i18n import MsgKey, set_language as set_ui_language, t


class LanguageSetter:

    @staticmethod
    def check_lang_in_text_mode(settings: Settings, repo: Repository):
        lang = repo.data.lang
        lang_drafts: dict[str, str] = settings.get_languages_settings().get_languages_with_drafts()
        if lang == "":
            options = lang_drafts.keys()
            print(f"\n{t(MsgKey.LANG_SELECT_DEFAULT_NOT_SET)}\n")
            while True:
                print(t(MsgKey.LANG_SELECT_PROMPT) + " ", end="")
                print(t(MsgKey.LANG_SELECT_OPTIONS_PREFIX) + ", ".join(options) + t(MsgKey.LANG_SELECT_OPTIONS_SUFFIX), end="", flush=True)
                print(":", end=" ")
                lang = input()
                if lang in options:
                    break
            repo.data.lang = lang
            RepositoryLoader(repo).save_config()
            
    def __init__(self, settings: Settings, repo: Repository, fman: FloatingManager):
        self.fman = fman
        self.rep = repo
        self.settings = settings

    def set_language(self):
        options: list[FloatingInputData] = []
        lang_drafts: dict[str, str] = self.settings.get_languages_settings().get_languages_with_drafts()
        keys = sorted(lang_drafts.keys())
        for lang in keys:
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
            .set_default_index(keys.index(self.rep.data.lang))
        )

    def toggle_ui_language(self):
        current = set_ui_language(self.settings.app.ui_language)
        next_lang = "en" if current == "pt-BR" else "pt-BR"
        self.settings.app.ui_language = next_lang
        set_ui_language(next_lang)
        self.settings.save_settings()
        self.fman.add_input(
            Floating()
            .bottom()
            .right()
            .put_text("")
            .put_text(t(MsgKey("ui.language_changed"), language=next_lang))
            .put_text("")
            .set_warning()
        )

class TextFunctor:
    def __init__(self, data: str):
        self.value = data
    
    def __call__(self):
        return RText(self.value)

class SetLangFunctor:
    def __init__(self, settings: Settings, rep: Repository, fman: FloatingManager, lang: str):
        self.rep = rep
        self.fman = fman
        self.value = lang
        self.settings = settings

    def __call__(self):
        self.rep.data.lang = self.value.strip()
        RepositoryLoader(self.rep).save_config()
        self.fman.add_input(
            Floating()
            .bottom()
            .right()
            .put_text("")
            .put_text("Linguagem alterada para " + self.value)
            .put_text("")
            .set_warning()
        )
