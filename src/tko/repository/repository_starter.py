from pathlib import Path
from tko.play.language_setter import LanguageSetter
from tko.util.rtext import RText
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths
import shutil
from tko.config.settings import Settings
from tko.repository.repository_loader import RepositoryLoader

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
            print(RText.parse(f"A linguagem do repositório foi definida como [y]{self.language}[.]."))
        else:
            LanguageSetter.check_lang_in_text_mode(self.settings, self.repo)
        
        RepositoryLoader(repo).save_config()

        return True

    def print_end_msg(self):
        print(RText.parse(f"Voce pode acessar o repositório com o comando [g]tko open[.]"))
    
    def create_repository(self) -> Repository | None:
        path_parents = RepositoryPaths.rec_search_for_repo_parents(self.folder)

        if path_parents is not None and path_parents.resolve() == self.folder.resolve():
            print(RText.parse(f"Já existe um repositório TKO na pasta [y]{self.folder.resolve()}[.]"))
            print(RText.parse(f"Deseja resetar o repositório? ([g]s[.]/[r]n[.]): "), end="")
            op = input()
            if op == "n":
                return None

        elif path_parents is not None:
            if self.folder != path_parents:
                print(RText.parse(f"Você está tentando criar um repositório dentro de outro, pois já existe rep em [r]{path_parents}[.]"))
                print(RText.parse("Você pode apagar o repositório antigo, criar seu repositório em outro lugar ou sobrescrever as configurações."))
            self.folder = path_parents
            print(RText.parse(f"Deseja sobrescrever as configurações do repositório em [y]{self.folder}[.] ? ([g]s[.]/[r]n[.]): "), end="")
            op = input()
            if op == "n":
                return None
        else:
            path_subdir_list = RepositoryPaths.rec_search_for_repo_subdir(self.folder)
            if len(path_subdir_list) > 0:
                print(RText.parse(f"Você está tentando criar um repositório TKO na pasta [y]{self.folder.resolve()}[.]"))
                print(RText.parse("Porém já existem repositórios TKO abaixo dessa pasta. Mova ou apague-os"))
                for path in path_subdir_list:
                    print(RText.parse(f"- [r]{path}[.]"))
                return None

        return Repository(self.folder)
    
    def create_empty_repo(self):
        source = self.repo.create_default_sandbox_source()
        self.repo.data.set_remote(source)
        print(f"Criando repositório vazio, como pasta para atividades locais")
    