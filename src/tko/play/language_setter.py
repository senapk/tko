from tko.floating import Floating
from tko.floating.floating_drop_down import FloatingDropDown
from tko.floating.floating_drop_down import FloatingInputData
from tko.floating.floating_manager import FloatingManager
from tko.repository.repository_config import RepositoryConfig
from tko.util.rt import RT
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.i18n import Msg, set_language as set_ui_language, SUPPORTED_LANGUAGES, t
from tko.util.console import Console

class _LangSetterMsg:
    UI_LANGUAGE_CHANGED = Msg(pt="Idioma da interface alterado para {language}", en="Interface language changed to {language}")
    LANGUAGE_CHANGED = Msg(pt="Linguagem alterada para {language}", en="Language changed to {language}")
    LANG_CHOOSE = Msg(pt="Escolha a extensão default para os rascunhos", en="Choose the default extension for drafts")
    RESET_TKO = Msg(pt="Reinicie o tko para aplicar as mudanças", 
                    en="Restart tko to apply changes")
    PROMPT = Msg(pt="Escolha entre as opções a seguir [[[y]{options}[]]]: ", 
                 en="Choose from the following options [[[y]{options}[]]]: ")
    UI_NOT_SET = Msg(pt="[g]Idioma[] padrão da UI ainda não foi definida.", 
                     en="Default [g]UI language[] has not been set yet.")
    PROG_LANGUAGE_NOT_SET = Msg(pt="[g]Linguagem de programação[] padrão ainda não foi definida.", 
                                en="Default [g]programming language[] has not been set yet.")

class LanguageSetter:
    @staticmethod
    def replace_lang_on_repo(options: list[str], repo:Repository) -> None:
        options = sorted(options)
        Console.print(_LangSetterMsg.PROG_LANGUAGE_NOT_SET)
        while True:
            Console.print(_LangSetterMsg.PROMPT, options=", ".join(options), flush=True, end="")
            lang = input()
            if lang in options:
                break
        repo.data.lang = lang
        RepositoryConfig(repo).save()

    @staticmethod
    def check_prog_lang_in_text_mode(settings: Settings, repo: Repository, selected: str | None = None) -> str:
        """
        If selected is provided, try use it as the language, otherwise check the repo data and if it's not set, prompt the user to choose one.
        """
        options: list[str] = list(settings.get_languages_settings().get_languages_with_drafts().keys())
        if selected is not None:
            # unchanged
            if selected in options and selected == repo.data.lang:
                return selected
            # change
            if selected in options:
                repo.data.lang = selected
                RepositoryConfig(repo).save()
                return selected
            # ask and change    
            LanguageSetter.replace_lang_on_repo(list(options), repo)
            return repo.data.lang
            
        # check if already set and valid
        if repo.data.lang in options:
            return repo.data.lang
        # ask and change
        LanguageSetter.replace_lang_on_repo(list(options), repo)
        return repo.data.lang
    
    @staticmethod
    def check_ui_lang_in_text_mode(settings: Settings, selected: str | None = None) -> str:
        lang_options: list[str] = list(SUPPORTED_LANGUAGES)
        lang = settings.app.ui_language if selected is None else selected
        changed = False
        if lang == "" or lang not in lang_options:
            options = sorted(lang_options)
            Console.print(_LangSetterMsg.UI_NOT_SET)
            while True:
                Console.print(_LangSetterMsg.PROMPT, options=", ".join(options), flush=True, end="")
                lang = input()
                if lang in options:
                    changed = True
                    break
        if changed:
            settings.app.ui_language = lang
            settings.save_settings()
        return lang
            
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
                .set_header(t(_LangSetterMsg.LANG_CHOOSE))
                .set_footer(t(_LangSetterMsg.RESET_TKO))
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
        # self.fman.add_input(
        #     Floating()
        #     .bottom()
        #     .right()
        #     .put_text("")
        #     .put_text(t(_LangSetterMsg.UI_LANGUAGE_CHANGED, language=next_lang))
        #     .put_text("")
        #     .set_warning()
        # )

class TextFunctor:
    def __init__(self, data: str):
        self.value = data
    
    def __call__(self):
        return RT(self.value)

class SetLangFunctor:
    def __init__(self, settings: Settings, rep: Repository, fman: FloatingManager, lang: str):
        self.rep = rep
        self.fman = fman
        self.value = lang
        self.settings = settings

    def __call__(self):
        self.rep.data.lang = self.value.strip()
        RepositoryConfig(self.rep).save()
        self.fman.add_input(
            Floating()
            .bottom()
            .right()
            .put_text("")
            .put_text(t(_LangSetterMsg.LANGUAGE_CHANGED, language=self.value))
            .put_text("")
            .set_warning()
        )
