"""Load a student repository, migrating its task data when required."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from tko.config.run_settings import RunSettings
from tko.repository.repository import Repository
from tko.repository.repository_builder import RepositoryBuilder
from tko.repository.task_data_format import MigrationRequiredError
from tko.repository.task_migration import TaskDataMigration
from tko.util.console import Console


class ReviewMigrationError(ValueError):
    """A student repository could not be migrated automatically."""


def load_review_repository(folder: Path, settings: RunSettings, *, announce: bool = True) -> Repository:
    run_settings: RunSettings = replace(settings, changedir=folder)

    def build() -> Repository:
        repo, _ = RepositoryBuilder(run_settings).verbose(False).load_config_and_game(True).build()
        if repo is None:
            raise ValueError(f"Não foi possível carregar o repositório TKO: {folder}")
        return repo

    try:
        return build()
    except MigrationRequiredError:
        if announce:
            Console.print(f"Migrando repositório do aluno {folder.name}...")
    try:
        TaskDataMigration(folder).inspect().apply()
        return build()
    except (ValueError, OSError, Warning) as error:
        raise ReviewMigrationError(f"Migração falhou para {folder.name}: {error}") from error
