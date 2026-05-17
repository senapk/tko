from pathlib import Path
from tko.play.language_setter import LanguageSetter
from tko.util.rtext import RText
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths
import shutil
from tko.config.settings import Settings
from tko.repository.repository_loader import RepositoryLoader
from tko.i18n import MsgKey, t

class RepositoryStarter:
    def __init__(self, settings: Settings, folder: Path | None, language: str | None = None):
        self.settings = settings
        # if folder is set, use folder, else use local folder.
        self.folder: Path = Path.cwd()
        if folder is not None:
            self.folder = folder
        self.language = language

    def execute(self) -> bool:
        repo = self.create_repository()
        if repo is None:
            return False
        
        self.repo = repo
        self.create_empty_repo()
        # erase cache folder to avoid conflicts
        cache_folder = repo.paths.cache_folder
        if cache_folder.exists():
            shutil.rmtree(cache_folder)
        cache_folder.mkdir(parents=True, exist_ok=True)
        if self.language is not None:
            repo.data.lang = self.language
            print(RText.parse(t(MsgKey.REPO_STARTER_LANGUAGE_SET, language=self.language)))
        else:
            LanguageSetter.check_lang_in_text_mode(self.settings, self.repo)
        
        RepositoryLoader(repo).save_config()

        return True

    def print_end_msg(self):
        print(RText.parse(t(MsgKey.REPO_STARTER_OPEN_HINT)))
    
    def create_repository(self) -> Repository | None:
        path_parents = RepositoryPaths.rec_search_for_repo_parents(self.folder)

        if path_parents is not None and path_parents.resolve() == self.folder.resolve():
            print(RText.parse(t(MsgKey.REPO_STARTER_EXISTS, folder=self.folder.resolve())))
            print(RText.parse(t(MsgKey.REPO_STARTER_RESET_PROMPT)), end="")
            op = input()
            if op == "n":
                return None

        elif path_parents is not None:
            if self.folder != path_parents:
                print(RText.parse(t(MsgKey.REPO_STARTER_INSIDE_OTHER_REPO, parent=path_parents)))
                print(RText.parse(t(MsgKey.REPO_STARTER_DEEP_REPO_WARN_2)))
            self.folder = path_parents
            print(RText.parse(t(MsgKey.REPO_STARTER_OVERWRITE_PROMPT, folder=self.folder)), end="")
            op = input()
            if op == "n":
                return None
        else:
            path_subdir_list = RepositoryPaths.rec_search_for_repo_subdir(self.folder)
            if len(path_subdir_list) > 0:
                print(RText.parse(t(MsgKey.REPO_STARTER_DEEP_REPO_WARN, folder=self.folder.resolve())))
                print(RText.parse(t(MsgKey.REPO_STARTER_DEEP_REPO_WARN_2)))
                for path in path_subdir_list:
                    print(RText.parse(f"- [r]{path}[.]"))
                return None

        return Repository(self.folder)
    
    def create_empty_repo(self):
        source = self.repo.create_default_sandbox_source()
        self.repo.data.set_remote(source)
        print(t(MsgKey.REPO_STARTER_EMPTY_REPO))
    