import shutil

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
            raise ValueError(f"Repositório não encontrado em {folder}")
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
            print(Text.format("- Rótulo: {y}", source.alias))
            print(Text.format("  - Link ou Caminho: {y}", source.get_url_link()))
            print(Text.format("  - File Path     : {y}", source.get_source_readme()))
            print(Text.format("  - Filtragem      : {y}", "Desativado" if source.filters is None else 'Ativado'))
            for f in source.filters or []:
                print(f"    - {f}")

    def del_source(self, alias: str) -> None:
        rep = self.rep
        sources = rep.data.get_sources()
        found = False
        for source in sources:
            if source.alias == alias:
                found = True
                if source.is_git_source():
                    cache_folder = source.get_source_cache_folder()
                    if os.path.exists(cache_folder):
                        shutil.rmtree(cache_folder)
                rep.data.del_source(alias)
                print(Text.format("Fonte {y} removida com sucesso.", alias))
                break
        if not found:
            raise Warning("fail: fonte não encontrada.")
        rep.save_config()

    def source_enable(self, alias: str, filters: list[str] | None = None) -> None:
        rep = self.rep
        sources = rep.data.get_sources()
        found = False
        for source in sources:
            if source.alias == alias:
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

    def add_source(self, alias: str, default_repo_aliases: str | None, clone_url: str | None, local_source_folder: str | None, filters: list[str] | None, writeable: bool, branch: str = "master") -> None:
        rep = self.rep
        if default_repo_aliases is not None:
            print(Text.format("Adicionando fonte remota apontando para repositório remoto {y}.", default_repo_aliases))
            url: str = ""
            settings = Settings()
            if not settings.has_alias_git(default_repo_aliases):
                raise Warning("fail: alias git remoto não encontrado.")
            url = settings.get_alias_git(default_repo_aliases)
            self.git_clone_repository(url, alias, filters, branch)
        elif local_source_folder is not None:
            print(Text.format("Adicionando fonte local apontando parao repositório {y}.", local_source_folder))
            source = os.path.abspath(local_source_folder)
            rep.data.set_source(RepSource(alias=alias).set_local_source(target=source).set_filters(filters).set_writeable(writeable))
        elif clone_url is not None:
            self.git_clone_repository(clone_url, alias, filters, branch)

        self.rep.save_config()
   

    def git_clone_repository(self, link: str, alias: str, filters: list[str] | None, branch: str) -> None:
        print(Text.format("Clonando repositório remoto {y}.", link))
        cache_path = self.rep.paths.get_cache_folder()
        target = os.path.join(cache_path, alias)
        if os.path.exists(target):
            shutil.rmtree(target)
        if not self.rep.clone_repository_git(link, target):
            return
        print(Text.format("Repositório clonado com sucesso em {y}.", target))
        self.rep.data.set_source(RepSource(alias=alias).set_git_source(target=link, branch=branch).set_filters(filters))


    def print_end_msg(self):
        rel_path = os.path.relpath(self.rep.paths.get_workspace_dir(), os.getcwd())
        print(Text.format("Voce pode acessar o repositório com o comando {g} {y}", "tko open", "<pasta>"))
        print(Text.format("Por exemplo: {g} {y}", "tko open", rel_path))
