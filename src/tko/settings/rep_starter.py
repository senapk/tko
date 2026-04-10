import os
from pathlib import Path
from tko.play.language_setter import LanguageSetter
from tko.util.text import Text
from tko.settings.repository import Repository
from tko.settings.rep_paths import RepPaths
import shutil
from tko.settings.settings import Settings
class RepStarter:
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
        self.create_empty_rep()
        # erase cache folder to avoid conflicts
        cache_folder = repo.paths.get_cache_folder()
        if os.path.exists(cache_folder):
            shutil.rmtree(cache_folder)
        os.makedirs(cache_folder, exist_ok=True)
        if self.language is not None:
            repo.data.lang = self.language
            print(Text.format("A linguagem do repositório foi definida como {y}.", self.language))
        else:
            LanguageSetter.check_lang_in_text_mode(self.settings, self.repo)
        
        repo.save_config()
        return True

    def print_end_msg(self):
        print(Text.format("Voce pode acessar o repositório com o comando {g} {y}", "tko open"))
    
    def create_repository(self) -> Repository | None:
        path_parents = RepPaths.rec_search_for_repo_parents(self.folder)

        if path_parents is not None and path_parents.resolve() == self.folder.resolve():
            print(Text.format("Já existe um repositório TKO na pasta {y}", self.folder.resolve()))
            print(Text.format("Deseja resetar o repositório? ({g}/{r}): ", "s", "n"), end="")
            op = input()
            if op == "n":
                return None

        elif path_parents is not None:
            if self.folder != path_parents:
                print(Text.format("Você está tentando criar um repositório dentro de outro, pois já existe rep em {r}.", path_parents))
                print(Text.format("Você pode apagar o repositório antigo, criar seu repositório em outro lugar ou sobrescrever as configurações."))
            self.folder = path_parents
            print(Text.format("Deseja sobrescrever as configurações do repositório em {y} ? ({g}/{r}): ", self.folder, "s", "n"), end="")
            op = input()
            if op == "n":
                return None
        else:
            path_subdir_list = RepPaths.rec_search_for_repo_subdir(self.folder)
            if len(path_subdir_list) > 0:
                print(Text.format("Você está tentando criar um repositório TKO na pasta {y}", self.folder.resolve()))
                print(Text.format("Porém já existem repositórios TKO abaixo dessa pasta. Mova ou apague-os"))
                for path in path_subdir_list:
                    print(Text.format("- {r}", path))
                return None

        return Repository(self.folder)
    
    def create_empty_rep(self):
        source = self.repo.create_default_sandbox_source()
        self.repo.data.set_source(source)
        folder = source.get_workspace()
        print(f"Criando repositório vazio, utilizando a pasta {folder} como pasta para atividades locais")
    