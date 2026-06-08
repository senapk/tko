from pathlib import Path

from tko.config.run_settings import RunSettings
from tko.repository.repository import Repository
from tko.repository.repository_builder import RepositoryBuilder

def load_repo(rs: RunSettings, show_warnings: bool = True, auto_load: bool = True) -> tuple[Repository | None, Path | None]:
    rb = RepositoryBuilder(rs)
    repo, root_dir = (rb.verbose(show_warnings)
                        .load_config_and_game(auto_load)
                        .build())
    return repo, root_dir