from tko.settings.rep_paths import RepPaths
from tko.settings.rep_source import RepSource
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.util.text import Text

import os

class RepSourceActions:
    def __init__(self, folder: str | None):
        # if folder is set, use folder, else use remote if remote, else .
        if folder is not None:
            folder = os.path.abspath(folder)
        else:
            folder = os.path.abspath(os.getcwd())

        path = RepPaths.rec_search_for_repo(folder)
        if path == "":
            raise ValueError("Repositório não encontrado")
        self.folder = folder
        self.rep = Repository(path).load_config()
    
    def list_sources(self):
        rep = self.rep
        sources = rep.data.get_sources()
        print("Você também pode configurar as fontes e filtros manualmente editando o arquivo:")
        print(Text.format("{y}", rep.paths.get_config_file()))
        if len(sources) == 0:
            print("Nenhuma fonte configurada")
            return
        print("Fontes configuradas:")
        for source in sources:
            print(Text.format("- Rótulo: {y}", source.database))
            print(Text.format("  - Link ou Caminho: {y}", source.link))
            print(Text.format("  - Filtragem      : {y}", "Desativado" if source.filters is None else 'Ativado'))
            for f in source.filters or []:
                print(f"    - {f}")

    def source_enable(self, alias: str, filters: list[str] | None = None) -> None:
        rep = self.rep
        sources = rep.data.get_sources()
        found = False
        for source in sources:
            if source.database == alias:
                found = True
                if filters is not None:
                    if source.filters is None:
                        source.filters = []
                    for f in filters:
                        if f not in source.filters:
                            source.filters.append(f)
                print(Text.format("Filtro {y} ativado com sucesso.", alias))
                break
        if not found:
            raise Warning("fail: fonte não encontrada.")
        rep.save_config()
            
    def add_source(self, remote: str | None, alias: str, link: str | None, filters: list[str] | None = None) -> None:
        rep = self.rep
        if link is None and remote is None:
            print("Você precisa informar o endereço da fonte")
        elif remote is not None:
            print(Text.format("Adicionando fonte remota apontando para repositório remoto {y}.", remote))
            source: str = ""
            settings = Settings()
            if not settings.has_alias_remote(remote):
                raise Warning("fail: alias remoto não encontrado.")
            source = settings.get_alias_remote(remote)
            rep.data.set_source(RepSource(database=remote, link=source, filters=filters))
        elif link is not None:
            if link.startswith("http"):
                print(Text.format("Adicionando fonte remota apontando para link remota {y}.", link))
                source = link
                rep.data.set_source(RepSource(database=alias, link=source, filters=filters))
            else:
                print(Text.format("Adicionando fonte local apontando para arquivo local {y}.", link))
                source = os.path.abspath(link)
                if source.startswith(self.folder):
                    source = os.path.relpath(source, os.path.dirname(rep.paths.get_config_file()))
                print("debug", source)
                rep.data.set_source(RepSource(database=alias, link=source, filters=filters))

        self.rep.save_config()
   

    def print_end_msg(self):
        rel_path = os.path.relpath(self.rep.paths.get_rep_dir(), os.getcwd())
        print(Text.format("Voce pode acessar o repositório com o comando {g} {y}", "tko open", "<pasta>"))
        print(Text.format("Por exemplo: {g} {y}", "tko open", rel_path))
