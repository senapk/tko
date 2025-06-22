import os
from tko.util.text import Text
from tko.util.decoder import Decoder
from tko.settings.repository import Repository
from tko.settings.rep_paths import RepPaths
from tko.settings.settings import Settings

class RepStarter:
    def __init__(self, remote: str | None, source: str | None, folder: str | None, language: str | None = None, database: str | None = None):
        self.folder: str = ""
        # if folder is set, use folder, else use remote if remote, else .
        if not self.set_folder(folder, remote):
            return

        rep = self.create_repository()
        if rep is None:
            return
        self.rep = rep

        if source is None and remote is None:
            print(Text.format("Nenhuma fonte foi informada, criando repositório vazio."))
            self.create_empty_rep()
        elif remote is not None:
            print(Text.format("Criando repositório apontando para repositório remoto {y}.", remote))
            self.source: str = ""
            settings = Settings()
            if not settings.has_alias_remote(remote):
                raise Warning("fail: alias remoto não encontrado.")
            self.source = settings.get_alias_remote(remote)
            rep.set_rep_source(self.source)
        elif source is not None:
            if source.startswith("http"):
                print(Text.format("Criando repositório apontando para link remota {y}.", source))
                self.source = source
            else:
                print(Text.format("Criando repositório apontando para arquivo local {y}.", source))
                self.source = os.path.abspath(source)
                if self.source.startswith(self.folder):
                    self.source = os.path.relpath(self.source, os.path.dirname(rep.paths.get_config_file()))
            rep.set_rep_source(self.source)
        if language is not None:
            rep.set_lang(language)
            print(Text.format("A linguagem do repositório foi definida como {y}.", language))
        if database is not None:
            rep.set_database_folder(database)
            print(Text.format("A pasta com as questões foi definida para {y}.", database))
        rep.save_config()
        self.print_end_msg()

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
        index = self.rep.paths.get_default_readme_path()
        self.rep.set_rep_source(index)
        print("Nenhuma fonte foi informada, utilizando o arquivo {} como fonte".format(index))
        if not os.path.exists(index):
            content = "# Repositório\n\n## Grupo\n\n### Missão\n\n- [ ] [#google Abra o google](https://www.google.com)\n"
            Decoder.save(index, content)