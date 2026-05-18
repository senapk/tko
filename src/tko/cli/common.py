from pathlib import Path

from tko.repository.git_cache import UpdateMode
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths
from tko.i18n import Msg, t


_CLI_COMMON_GLOBAL_CACHE = Msg(
    pt="Usando cache global em: {cache}",
    en="Using global cache at: {cache}",
)
_CLI_COMMON_NO_REPO = Msg(
    pt="Nenhum repositório TKO encontrado.",
    en="No TKO repository found.",
)

def load_repo(dir_path: Path, show_warnings: bool = True, auto_load: bool = True, global_cache: bool = False, force_update: bool = False, force_offline: bool = False) -> tuple[Repository | None, Path | None, UpdateMode]:
    
    if global_cache:
        RepositoryPaths.use_global_cache_folder = True
        print(t(_CLI_COMMON_GLOBAL_CACHE, cache=RepositoryPaths('').cache_folder))
        
    dir_parent = RepositoryPaths.rec_search_for_repo_parents(dir_path)
    if dir_parent is not None:
        mode = UpdateMode.IF_OLDER
        if force_update:
            mode = UpdateMode.ALWAYS
        elif force_offline:
            mode = UpdateMode.NEVER
            
        repo = Repository(dir_parent, update_mode=mode, recursive_search=False)
        if auto_load:
            from tko.repository.repository_loader import RepositoryLoader
            from tko.repository.game_coordinator import GameCoordinator
            RepositoryLoader(repo).load_config()
            GameCoordinator(repo).load_game(verbose=True)
        return repo, dir_parent, mode

    if show_warnings:
        print(t(_CLI_COMMON_NO_REPO))
    return None, None, UpdateMode.IF_OLDER
