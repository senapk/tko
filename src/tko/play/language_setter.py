from tko.config.settings import Settings
from tko.i18n import SUPPORTED_LANGUAGES, set_language as set_ui_language
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader


class LanguageSetter:
    """Persist language choices; Textual owns the interactive selection UI."""

    @staticmethod
    def check_prog_lang_in_text_mode(
        settings: Settings, repo: Repository, selected: str | None = None
    ) -> str:
        options = sorted(settings.get_languages_settings().get_languages_with_drafts())
        if not options:
            return repo.data.lang
        language = selected if selected in options else repo.data.lang
        if language not in options:
            language = options[0]
        if language != repo.data.lang:
            repo.data.lang = language
            RepositoryLoader(repo).save()
        return language

    @staticmethod
    def check_ui_lang_in_text_mode(settings: Settings, selected: str | None = None) -> str:
        language = selected if selected in SUPPORTED_LANGUAGES else settings.app.ui_language
        if language not in SUPPORTED_LANGUAGES:
            language = "pt-BR"
        if language != settings.app.ui_language:
            settings.app.ui_language = language
            settings.save_settings()
        return language

    def __init__(self, settings: Settings, repo: Repository):
        self.rep = repo
        self.settings = settings

    def toggle_ui_language(self) -> None:
        current = set_ui_language(self.settings.app.ui_language)
        next_language = "en" if current == "pt-BR" else "pt-BR"
        self.settings.app.ui_language = next_language
        set_ui_language(next_language)
        self.settings.save_settings()
