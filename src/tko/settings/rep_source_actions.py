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
    
    def remote_ls(self):
        rep = self.rep
        sources = rep.data.get_sources()
        print("Você também pode configurar as fontes e filtros manualmente editando o arquivo:")
        print(Text.format("{y}", rep.paths.get_config_file()))
        if len(sources) == 0:
            print("Nenhuma fonte configurada")
            return
        print("Fontes configuradas:")
        for source in sources:
            print(Text.format("- Rótulo: {y}", source.name))
            print(Text.format("  - Link ou Caminho: {y}", source.get_url_link()))
            print(Text.format("  - File Path     : {y}", source.get_source_readme()))
            print(Text.format("  - Filtragem      : {y}", "Desativado" if source.quests is None else 'Ativado'))
            for f in source.quests or []:
                print(f"    - {f}")

    def remote_rm(self, alias: str) -> None:
        rep = self.rep
        sources = rep.data.get_sources()
        found = False
        for source in sources:
            if source.name == alias:
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

    def remote_filter(self, alias: str, quests: list[str] | None = None, tasks: list[str] | None = None, clear: bool = False) -> None:
        rep = self.rep
        sources = rep.data.get_sources()
        found = False
        for source in sources:
            if source.name == alias:
                found = True
                if quests is not None:
                    if source.quests is None:
                        source.quests = []
                    for f in quests:
                        if f not in source.quests:
                            source.quests.append(f)
                if tasks is not None:
                    if source.tasks is None:
                        source.tasks = []
                    for f in tasks:
                        if f not in source.tasks:
                            source.tasks.append(f)
                if clear:
                    source.quests = None
                    source.tasks = None
                print(Text.format("Filtros {y} atualizados com sucesso.", alias))
                break
        if not found:
            raise Warning("fail: fonte não encontrada.")
        rep.save_config()

    def remote_add(self, name: str, remote_default: str | None, remote_url: str | None, remote_dir: str | None, quest_filter: list[str] | None, task_filter: list[str] | None, writeable: bool, branch: str = "master") -> None:
        # check if name already exists
        if any(source.name == name for source in self.rep.data.get_sources()):
            raise Warning("fail: fonte com esse nome já existe.")

        rep = self.rep
        if remote_default is not None:
            print(Text.format("Adicionando fonte remota apontando para repositório remoto {y}.", remote_default))
            url: str = ""
            settings = Settings()
            if not settings.has_alias_git(remote_default):
                raise Warning("fail: alias git remoto não encontrado.")
            url = settings.get_alias_git(remote_default)
            self.git_clone_repository(url, name, quest_filter, branch)
        elif remote_dir is not None:
            print(Text.format("Adicionando fonte local apontando parao repositório {y}.", remote_dir))
            source = os.path.abspath(remote_dir)
            rep.data.set_source(RepSource(alias=name).set_local_source(target=source).set_filters(quests=quest_filter, tasks=task_filter).set_writeable(writeable))
        elif remote_url is not None:
            self.git_clone_repository(remote_url, name, quest_filter, branch)

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
        print(Text.format("Voce pode acessar o repositório com o comando {g}", "tko open"))
        
