import os
from pathlib import Path
from tko.play.language_setter import LanguageSetter
from tko.util.text import Text
from tko.settings.repository import Repository
from tko.settings.rep_paths import RepPaths
import shutil
class RepStarter:
    def __init__(self, folder: Path | None, language: str | None = None):
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
            LanguageSetter.check_lang_in_text_mode(self.repo)
        
        repo.save_config()
        return True

    def print_end_msg(self):
        print(Text.format("Voce pode acessar o repositório com o comando {g} {y}", "tko open"))
    
    def create_repository(self) -> Repository | None:
        path_old = RepPaths.rec_search_for_repo(self.folder)
        if path_old is not None:
            if self.folder != path_old:
                print(Text.format("Você está tentando criar um rep dentro de outro, pois já existe rep em {r}.", path_old))
                print(Text.format("Você pode apagar o repositório antigo removendo a pasta {r:}.", os.path.join(path_old, ".tko")))
                print(Text.format("Ou sobrescrever as configurações de  {r:}.", os.path.join(path_old, ".tko")))
            self.folder = path_old
            print(Text.format("Deseja sobrescrever as configurações do repositório em {y} ? ({g}/{r}): ", self.folder, "s", "n"), end="")
            op = input()
            if op == "n":
                return None
        return Repository(self.folder)
    
    def create_empty_rep(self):
        source = self.repo.get_student_sandbox()
        self.repo.data.set_source(source)
        folder = source.get_source_workspace()
        print(f"Criando repositório vazio, utilizando a pasta {folder} como pasta para atividades locais")
    