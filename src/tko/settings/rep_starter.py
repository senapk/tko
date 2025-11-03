import os
from tko.util.text import Text
from tko.settings.repository import Repository
from tko.settings.rep_paths import RepPaths
import shutil
class RepStarter:
    def __init__(self, folder: str | None, language: str | None = None):
        # if folder is set, use folder, else use local folder.
        self.folder: str = os.path.abspath(os.getcwd())
        if folder is not None:
            self.folder = os.path.abspath(folder)
        self.language = language

    def execute(self) -> bool:
        rep = self.create_repository()
        if rep is None:
            return False
        
        self.rep = rep
        self.create_empty_rep()
        # erase cache folder to avoid conflicts
        cache_folder = rep.paths.get_cache_folder()
        if os.path.exists(cache_folder):
            shutil.rmtree(cache_folder)
        os.makedirs(cache_folder, exist_ok=True)
        if self.language is not None:
            rep.data.lang = self.language
            print(Text.format("A linguagem do repositório foi definida como {y}.", self.language))
        
        rep.save_config()
        return True

    def print_end_msg(self):
        rel_path = os.path.relpath(self.rep.paths.get_rep_dir(), os.getcwd())
        print(Text.format("Voce pode acessar o repositório com o comando {g} {y}", "tko open", "<pasta>"))
        print(Text.format("Por exemplo: {g} {y}", "tko open", rel_path))

    def set_folder(self, folder: str | None, remote: str | None) -> bool:
        if folder is not None:
            self.folder = os.path.abspath(folder)
            return True
        
        self.folder = os.path.abspath(os.getcwd())
        if remote is not None:
            self.folder = os.path.join(self.folder, remote)
        print(Text.format("A pasta onde deve ser criada o repositório {r:não} foi informada."))
        print(Text.format("Deseja criar o repositório na pasta {y} ? ({g}/{r}): ", self.folder, "s", "n"), end="")
        op = input()
        if op == "n":
            return False
        return True
    
    def create_repository(self) -> Repository | None:
        path_old = RepPaths.rec_search_for_repo(self.folder)
        if path_old != "":
            if self.folder != path_old:
                print(Text.format("Você está tentando criar um rep dentro de outro, pois já existe rep em {r}.", path_old))
                print(Text.format("Você pode apagar o repositório antigo removendo a pasta {r:}.", os.path.join(path_old, ".tko")))
                print(Text.format("Ou sobrescrever as configurações de  {r:}.", os.path.join(path_old, ".tko")))
            self.folder = path_old
            print(Text.format("Deseja sobrescrever as configurações do repositório em {y} ? ({g}/{r}): ", self.folder, "s", "n"), end="")
            op = input()
            if op == "n":
                return None
        return Repository(os.path.abspath(self.folder))
    
    def create_empty_rep(self):
        source = self.rep.get_default_local_source()
        self.rep.data.set_source(source)
        folder = source.get_local_database_path()
        print(f"Criando repositório vazio, utilizando a pasta {folder} como pasta para atividades locais")
    