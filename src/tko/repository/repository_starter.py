from pathlib import Path
from tko.play.language_setter import LanguageSetter
from tko.util.rt import RT
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths
import shutil
from tko.config.settings import Settings
from tko.repository.repository_loader import RepositoryLoader
from tko.i18n import Msg, t


_REPO_STARTER_LANGUAGE_SET = Msg(
    pt="A linguagem do repositório foi definida como <{language}:y>.",
    en="Repository language set to <{language}:y>.",
)
_REPO_STARTER_OPEN_HINT = Msg(
    pt="Voce pode acessar o repositório com o comando <tko open:g>",
    en="You can access the repository with the command <tko open:g>",
)
_REPO_STARTER_EXISTS = Msg(
    pt="Já existe um repositório TKO na pasta <{folder}:y>",
    en="A TKO repository already exists in folder <{folder}:y>",
)
_REPO_STARTER_RESET_PROMPT = Msg(
    pt="Deseja resetar o repositório? (<s:g>/<n:r>): ",
    en="Do you want to reset the repository? (<y:g>/<n:r>): ",
)
_REPO_STARTER_INSIDE_OTHER_REPO = Msg(
    pt="Você está tentando criar um repositório dentro de outro, pois já existe rep em <{parent}:r>",
    en="You are trying to create a repository inside another one, because there is already a repo in <{parent}:r>",
)
_REPO_STARTER_DEEP_REPO_WARN_2 = Msg(
    pt="Porém já existem repositórios TKO abaixo dessa pasta. Mova ou apague-os",
    en="But there are already TKO repositories below that folder. Move or delete them",
)
_REPO_STARTER_OVERWRITE_PROMPT = Msg(
    pt="Deseja sobrescrever as configurações do repositório em <{folder}:y> ? (<s:g>/<n:r>): ",
    en="Do you want to overwrite the repository settings in <{folder}:y> ? (<y:g>/<n:r>): ",
)
_REPO_STARTER_DEEP_REPO_WARN = Msg(
    pt="Você está tentando criar um repositório TKO na pasta <{folder}:y>",
    en="You are trying to create a TKO repository in folder <{folder}:y>",
)
_REPO_STARTER_EMPTY_REPO = Msg(
    pt="Criando repositório vazio, como pasta para atividades locais",
    en="Creating empty repository, as a folder for local activities",
)

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
            print(RT.parse(t(_REPO_STARTER_LANGUAGE_SET, language=self.language)))
        else:
            LanguageSetter.check_lang_in_text_mode(self.settings, self.repo)
        
        RepositoryLoader(repo).save_config()

        return True

    def print_end_msg(self):
        print(RT.parse(t(_REPO_STARTER_OPEN_HINT)))
    
    def create_repository(self) -> Repository | None:
        path_parents = RepositoryPaths.rec_search_for_repo_parents(self.folder)

        if path_parents is not None and path_parents.resolve() == self.folder.resolve():
            print(RT.parse(t(_REPO_STARTER_EXISTS, folder=self.folder.resolve())))
            print(RT.parse(t(_REPO_STARTER_RESET_PROMPT)), end="")
            op = input()
            if op == "n":
                return None

        elif path_parents is not None:
            if self.folder != path_parents:
                print(RT.parse(t(_REPO_STARTER_INSIDE_OTHER_REPO, parent=path_parents)))
                print(RT.parse(t(_REPO_STARTER_DEEP_REPO_WARN_2)))
            self.folder = path_parents
            print(RT.parse(t(_REPO_STARTER_OVERWRITE_PROMPT, folder=self.folder)), end="")
            op = input()
            if op == "n":
                return None
        else:
            path_subdir_list = RepositoryPaths.rec_search_for_repo_subdir(self.folder)
            if len(path_subdir_list) > 0:
                print(RT.parse(t(_REPO_STARTER_DEEP_REPO_WARN, folder=self.folder.resolve())))
                print(RT.parse(t(_REPO_STARTER_DEEP_REPO_WARN_2)))
                for path in path_subdir_list:
                    print(RT.parse("- <$:r>", path))
                return None

        return Repository(self.folder)
    
    def create_empty_repo(self):
        source = self.repo.create_default_sandbox_source()
        self.repo.data.set_remote(source)
        print(t(_REPO_STARTER_EMPTY_REPO))
    