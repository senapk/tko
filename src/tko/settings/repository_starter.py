import os
from tko.util.text import Text
from tko.util.decoder import Decoder
from tko.settings.repository import Repository
from tko.settings.settings import Settings

class RepStarter:
    def __init__(self, remote: str | None, source: str | None, folder: str | None):
        self.folder: str = ""
        if not self.set_folder(folder, remote):
            return

        rep = self.createRepository()
        if rep is None:
            return
        self.rep = rep

        if source is None and remote is None:
            self.create_empty_rep()
            rep.save_config()
            self.print_end_msg()
            return
        
        if remote is not None:
            self.source: str = ""
            settings = Settings()
            if not settings.has_alias_remote(remote):
                raise Warning("fail: alias remoto não encontrado.")
            self.source = settings.get_alias_remote(remote)
            rep.set_rep_source(self.source)
            rep.save_config()
            self.print_end_msg()
            return
        
        if source is not None:
            self.source = os.path.abspath(source)
            if self.source.startswith(self.folder):
                self.source = os.path.relpath(self.source, os.path.dirname(rep.get_config_file()))
            rep.set_rep_source(self.source)
            rep.save_config()
            self.print_end_msg()
            return
    
    def print_end_msg(self):
        rel_path = os.path.relpath(self.rep.root_folder, os.getcwd())
        print(Text.format("Voce pode acessar o repositório com o comando {g} {y}", "tko open", "<pasta>"))
        print(Text.format("Por exemplo: {g} {y}", "tko open", rel_path))

    def set_folder(self, folder: str | None, remote: str | None) -> bool:
        if folder is not None:
            self.folder = os.path.abspath(folder)
            return True
        
        self.folder = os.path.abspath(os.getcwd())
        if remote is not None:
            self.folder = os.path.join(self.folder, remote)
        print(Text.format("A pasta onde deve ser criada o repositório {r} foi informada.", "não"))
        print(Text.format("Deseja criar o repositório na pasta {y} ? ({g}/{r}): ", self.folder, "s", "n"), end="")
        op = input()
        if op == "n":
            return False
        return True
    
    def createRepository(self) -> Repository | None:
        path_old = Repository.rec_search_for_repo(self.folder)
        if path_old != "":
            self.folder = path_old
            print(Text.format("Já existe um repositório em {r}.", path_old))
            print(Text.format("Deseja sobrescrever as configurações do repositório em {y} ? ({g}/{r}): ", self.folder, "s", "n"), end="")
            op = input()
            if op == "n":
                return None
        return Repository(os.path.abspath(self.folder))
    
    def create_empty_rep(self):
        index = self.rep.get_default_readme_path()
        self.rep.set_rep_source(index)
        print("Nenhuma fonte foi informada, utilizando o arquivo {} como fonte".format(index))
        if not os.path.exists(index):
            content = "# Repositório\n\n## Grupo\n\n### Missão\n\n- [ ] [#google Abra o google](https://www.google.com)\n"
            Decoder.save(index, content)