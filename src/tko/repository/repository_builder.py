from tko.config.run_settings import RunSettings
from tko.config.user_data import UserData
from tko.i18n import Msg
from tko.repository.git_cache import GitCache
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths

from pathlib import Path
from tko.util.console import Console

_CLI_COMMON_NO_REPO = Msg(
    pt="Nenhum repositório TKO encontrado.",
    en="No TKO repository found.",
)

class RepositoryBuilder:
    def __init__(self, rs: RunSettings):
        
        self._rs = rs
        self._dir_path: Path = rs.changedir
        self._verbose: bool = True
        self._load_config_and_game: bool = True

    def verbose(self, value: bool = True):
        self._verbose = value
        return self

    def load_config_and_game(self, value: bool = True):
        self._load_config_and_game = value
        return self

    def build(self) -> tuple[Repository | None, Path]:
        root_dir = RepositoryPaths.rec_search_for_repo_parents(self._dir_path)
        if root_dir is None:
            if self._verbose:
                Console.print(str(_CLI_COMMON_NO_REPO))
            return None, Path()
        self._root_dir = root_dir
        git_cache = GitCache(cache_dir=UserData.global_cache_dir(), update_mode=self._rs.update_mode)
        repo = Repository(root_dir, rs=self._rs, git_cache=git_cache, recursive_search=False)
        if self._load_config_and_game:
            from tko.repository.repository_config import RepositoryConfig
            from tko.repository.game_coordinator import GameCoordinator
            RepositoryConfig(repo).load()
            GameCoordinator(repo).load_game()
        return repo, root_dir