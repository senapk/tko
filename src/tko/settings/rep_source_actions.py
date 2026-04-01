from tko.settings.rep_source import RepSource
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.util.text import Text
from pathlib import Path

class RepSourceActions:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo

    def remote_list(self):
        rep = self.repo
        sources = rep.data.get_sources()
        print("Você também pode configurar as fontes e filtros manualmente editando o arquivo:")
        print(Text.format("{y}", rep.paths.get_config_file()))
        if len(sources) == 0:
            print("Nenhuma fonte configurada")
            return
        print("Fontes configuradas:")
        for source in sources:
            self.show_source(source)
    
    def show_source(self, source: RepSource):
        print(Text.format("- Rótulo: {y}", source.name))
        print(Text.format("  - Link ou Caminho: {y}", source.get_url_link()))
        print(Text.format("  - File Path     : {y}", source.get_source_readme()))
        print(Text.format("  - Filtro Quests : {y}", "Desativado" if source.quests is None else 'Ativado'))
        if source.quests is not None:
            for f, v in source.quests.items():
                print(f"    - {f}: {v}")
        print(Text.format("  - Filtro Tasks  : {y}", "Desativado" if source.tasks is None else 'Ativado'))
        if source.tasks is not None:
            for f, v in source.tasks.items():
                print(f"    - {f}: {v}")

    def remote_rm(self, alias: str) -> None:
        rep = self.repo
        sources = rep.data.get_sources()
        found = False
        for source in sources:
            if source.name == alias:
                found = True
                rep.data.del_source(alias)
                print(Text.format("Fonte {y} removida com sucesso.", alias))
                break
        if not found:
            raise Warning("fail: fonte não encontrada.")
        rep.save_config()

    def remote_filter(self, alias: str, filter_quest: list[str] | None = None, filter_task: list[str] | None = None, clear: bool = False, filter_to: str | None = None) -> None:
        rep = self.repo
        source = rep.data.get_source(alias)
        if source is None:
            raise Warning("fail: fonte não encontrada.")
        change: bool = False

        if filter_quest is not None:
            if source.quests is None:
                source.quests = {}
            for f in filter_quest:
                if f not in source.quests:
                    change = True
                    source.quests[f] = filter_to if filter_to is not None else ""
            
        if filter_task is not None:
            if source.tasks is None:
                source.tasks = {}
            for f in filter_task:
                if f not in source.tasks:
                    change = True
                    source.tasks[f] = filter_to if filter_to is not None else ""
        if clear:
            change = True
            source.quests = None
            source.tasks = None
        
        # if not quests and not tasks and not clear:
        self.show_source(source)
        if change:
            print(Text.format("Filtros {y} atualizados com sucesso.", alias))
            rep.save_config()

    def fix_filter(self, source: list[str] | None, destiny: str | None) -> dict[str, str] | None:
        if source is None:
            return None
        return {s: destiny if destiny is not None else "" for s in source}

    def remote_add(
            self, 
            name: str, 
            remote_default: str | None, 
            remote_url: str | None, 
            remote_dir: str | None, 
            filter_quest: list[str] | None, 
            filter_task: list[str] | None, 
            filter_to: str | None,
            writeable: bool, branch: str = "master"
            ) -> None:
        
        if any(source.name == name for source in self.repo.data.get_sources()):
            raise Warning("fail: fonte com esse nome já existe.")

        repo = self.repo
        if remote_default is not None:
            print(Text.format("Adicionando fonte remota apontando para repositório git remoto {y}.", remote_default))
            url: str = ""
            settings = self.settings
            if not settings.has_alias_git(remote_default):
                raise Warning("fail: alias git remoto não encontrado.")
            url = settings.get_alias_git(remote_default)
            self.git_clone_repository(url)
            self.repo.data.set_source(RepSource(alias=name)
                                      .set_git_source(target=url, branch=branch)
                                      .set_filters(self.fix_filter(filter_quest, filter_to), self.fix_filter(filter_task, filter_to))
                                      .set_writeable(writeable))
        elif remote_dir is not None:
            dir_path = Path(remote_dir)
            if not dir_path.exists() or not dir_path.is_dir():
                raise Warning("fail: diretório remoto não encontrado.")
            print(Text.format("Adicionando fonte remota apontando parao repositório no diretorio {y}.", dir_path))
            repo.data.set_source(RepSource(alias=name)
                                 .set_local_source(target=dir_path)
                                 .set_filters(quests=self.fix_filter(filter_quest, filter_to), tasks=self.fix_filter(filter_task, filter_to))
                                 .set_writeable(writeable))
        elif remote_url is not None:
            print(Text.format("Adicionando fonte remota apontando para repositório git remoto {y}.", remote_url))
            self.git_clone_repository(remote_url)
            self.repo.data.set_source(RepSource(alias=name)
                                       .set_git_source(target=remote_url, branch=branch)
                                       .set_filters(self.fix_filter(filter_quest, filter_to), self.fix_filter(filter_task, filter_to))
                                       .set_writeable(writeable))

        self.repo.save_config()
   

    def git_clone_repository(self, link: str) -> None:
        print(Text.format("Clonando repositório remoto {y}.", link))
        _ = self.repo.cache.get(link, force_update=True)
        print(Text.format("Repositório {y} clonado com sucesso.", link))
        


    def print_end_msg(self):
        print(Text.format("Voce pode acessar o repositório com o comando {g}", "tko open"))
        
