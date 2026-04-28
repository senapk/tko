from pathlib import Path
from typing import Tuple, Optional

def load_repo(dir_path: Path, show_warnings: bool = True, auto_load: bool = True, global_cache: bool = False, force_update: bool = False, force_offline: bool = False):
    from tko.repository.rep_paths import RepPaths
    from tko.repository.git_cache import GitCache
    from tko.repository.repository import Repository
    
    if global_cache:
        RepPaths.use_global_cache_folder = True
        print(f"Usando cache global em: {RepPaths('').get_cache_folder()}")
        
    dir_parent = RepPaths.rec_search_for_repo_parents(dir_path)
    if dir_parent is not None:
        mode = GitCache.UpdateMode.IF_OLDER
        if force_update:
            mode = GitCache.UpdateMode.ALWAYS
        elif force_offline:
            mode = GitCache.UpdateMode.NEVER
            
        repo = Repository(dir_parent, update_mode=mode, recursive_search=False)
        if auto_load:
            from tko.repository.repository_loader import RepositoryLoader
            from tko.repository.game_coordinator import GameCoordinator
            RepositoryLoader(repo).load_config()
            GameCoordinator(repo).load_game(verbose=True)
        return repo, dir_parent

    if show_warnings:
        print("Nenhum repositório TKO encontrado.")
    return None, None
