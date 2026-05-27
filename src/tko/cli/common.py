from pathlib import Path

from tko.repository.git_cache import UpdateMode
from tko.repository.repository import Repository
from tko.repository.repository_builder import RepositoryBuilder

def load_repo(dir_path: Path, show_warnings: bool = True, auto_load: bool = True, global_cache: bool = False, force_update: bool = False, force_offline: bool = False) -> tuple[Repository | None, Path | None, UpdateMode]:
    rb = RepositoryBuilder()
    repo, root_dir = (rb.dir_path(dir_path)
                        .verbose(show_warnings)
                        .load_config_and_game(auto_load)
                        .global_cache(global_cache)
                        .force_offline(force_offline)
                        .force_update(force_update)
                        .build())
    return repo, root_dir, rb.update_mode