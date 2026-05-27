from tko.i18n import t, Msg
from tko.repository.git_cache import UpdateMode
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths


from pathlib import Path

_CLI_COMMON_GLOBAL_CACHE = Msg(
    pt="Usando cache global em: {cache}",
    en="Using global cache at: {cache}",
)
_CLI_COMMON_NO_REPO = Msg(
    pt="Nenhum repositório TKO encontrado.",
    en="No TKO repository found.",
)

class RepositoryBuilder:
    def __init__(self):
        self._dir_path: Path = Path()
        self._verbose: bool = True
        self._load_config_and_game: bool = True
        self._use_global_cache: bool = False
        self._force_update: bool = False
        self._force_offline: bool = False

    def global_cache(self, value: bool = True):
        self._use_global_cache = value
        return self

    def verbose(self, value: bool = True):
        self._verbose = value
        return self

    def load_config_and_game(self, value: bool = True):
        self._load_config_and_game = value
        return self

    def dir_path(self, value: Path):
        self._dir_path = value
        return self

    def force_update(self, value: bool = True):
        self._force_update = value
        return self

    def force_offline(self, value: bool = True):
        self._force_offline = value
        return self

    @property
    def update_mode(self):
        mode = UpdateMode.IF_OLDER
        if self._force_update:
            mode = UpdateMode.ALWAYS
        elif self._force_offline:
            mode = UpdateMode.NEVER
        return mode

    def build(self) -> tuple[Repository | None, Path]:
        if self._use_global_cache:
            RepositoryPaths.use_global_cache_folder = True
            print(t(_CLI_COMMON_GLOBAL_CACHE, cache=RepositoryPaths('').cache_folder))

        root_dir = RepositoryPaths.rec_search_for_repo_parents(self._dir_path)
        if root_dir is None:
            if self._verbose:
                print(t(_CLI_COMMON_NO_REPO))
            return None, Path()
        self._root_dir = root_dir

        repo = Repository(root_dir, update_mode=self.update_mode, recursive_search=False)
        if self._load_config_and_game:
            from tko.repository.repository_config import RepositoryConfig
            from tko.repository.game_coordinator import GameCoordinator
            RepositoryConfig(repo).load()
            GameCoordinator(repo).load_game(verbose=self._verbose)
        return repo, root_dir