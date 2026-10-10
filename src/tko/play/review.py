"""Open student repositories one at a time in the normal TKO interface."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from tko.config.settings import Settings
from tko.play.language_setter import LanguageSetter
from tko.play.review_context import ReviewContext, ReviewLocation, ReviewNavigation, ReviewTarget
from tko.play.review_loader import ReviewMigrationError
from tko.play.review_overview import ReviewOverviewService
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths
from tko.repository.repository_watcher import RepositoryWatcher
from tko.ui_textual.app import TkoApp
from tko.util.console import Console


class ReviewFolderError(ValueError):
    """The requested class folder cannot be browsed."""


def student_repositories(parent: Path) -> list[Path]:
    """Return direct child workspaces in a stable order."""
    if not parent.is_dir():
        raise ReviewFolderError(f"Pasta não encontrada: {parent}")
    children: list[Path] = []
    for child in parent.iterdir():
        if not child.is_dir() or child.is_symlink():
            continue
        config = child / RepositoryPaths.CONFIG_FOLDER
        if (config / RepositoryPaths.CFG_FILE).is_file() or (config / RepositoryPaths.LEGACY_CFG_FILE).is_file():
            children.append(child.resolve())
    return sorted(children, key=lambda path: (path.name.casefold(), path.name))


class ReviewSession:
    def __init__(self, settings: Settings, parent: Path) -> None:
        self.settings: Settings = settings
        self.repositories: list[Path] = student_repositories(parent)
        self.context: ReviewContext = ReviewContext()
        self.overview: ReviewOverviewService = ReviewOverviewService(self.repositories, settings.rs)

    def run(self) -> None:
        if not self.repositories:
            raise ReviewFolderError("Nenhum repositório TKO encontrado nas subpastas imediatas.")
        original_dir: Path = Path.cwd()
        original_changedir: Path = self.settings.rs.changedir
        index: int = 0
        direction: int = 1
        skipped: dict[Path, str] = {}
        try:
            while 0 <= index < len(self.repositories):
                try:
                    result: ReviewNavigation | ReviewTarget | None = self._visit(index)
                except ReviewMigrationError as error:
                    message: str = str(error)
                    skipped[self.repositories[index]] = message
                    Console.print(message)
                    index += direction
                    continue
                if result is None:
                    return
                self.overview.invalidate(index)
                if isinstance(result, ReviewTarget):
                    direction = 1 if result.index >= index else -1
                    index = result.index
                    continue
                direction = result.delta
                index += direction
        finally:
            os.chdir(original_dir)
            self.settings.rs.changedir = original_changedir
            if skipped:
                Console.print(f"Repositórios não abertos por falha na migração: {len(skipped)}")
                for message in skipped.values():
                    Console.print(message)

    def _visit(self, index: int) -> ReviewNavigation | ReviewTarget | None:
        folder: Path = self.repositories[index]
        self.settings.rs.changedir = folder
        os.chdir(folder)
        repo: Repository = self._load_repo(folder)
        return self._open_repo(repo, index)

    def _load_repo(self, folder: Path) -> Repository:
        return self.overview.load_repository(folder)

    def _open_repo(self, repo: Repository, index: int) -> ReviewNavigation | ReviewTarget | None:
        LanguageSetter.check_prog_lang_in_text_mode(self.settings, repo)
        watcher: RepositoryWatcher = RepositoryWatcher(repo).start_watching(
            log_audit=repo.audit.enabled,
            audit_verbose=True,
            audit_interval_seconds=repo.audit.interval_seconds,
        )
        location = ReviewLocation(repo.root_dir.name, index, len(self.repositories))
        try:
            while True:
                outcome: Callable[[], None] | ReviewNavigation | ReviewTarget | None = TkoApp(
                    self.settings, repo, watcher, review_context=self.context,
                    review_location=location, review_overview=self.overview,
                ).run()
                if outcome is None or isinstance(outcome, (ReviewNavigation, ReviewTarget)):
                    return outcome
                outcome()
        finally:
            watcher.stop_watching()
