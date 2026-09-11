from __future__ import annotations

from tko.config.settings import Settings
from tko.play.language_setter import LanguageSetter
from tko.repository.repository import Repository
from tko.repository.repository_watcher import RepositoryWatcher


class Play:
    """Repository browser entry point backed by Textual.

    The previous class owned a terminal loop and calculated every window's
    coordinates itself. Presentation now lives in ``TkoApp``; this class only
    preserves the public command-layer contract.
    """

    def __init__(self, settings: Settings, repo: Repository, watcher: RepositoryWatcher | None):
        self.settings = settings
        self.repo = repo
        self.watcher = watcher
        self._need_update = False

    def display_need_update(self) -> None:
        self._need_update = True

    def play(self) -> None:
        LanguageSetter.check_prog_lang_in_text_mode(self.settings, self.repo)
        from tko.ui_textual import TkoApp

        while True:
            action = TkoApp(
                self.settings,
                self.repo,
                self.watcher,
                need_update=self._need_update,
            ).run()
            if action is None:
                return
            action()
