import logging
from tko.repository.remote import Remote
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.repository.repository_loader import RepositoryLoader
from tko.util.rtext import RText
from pathlib import Path


logger = logging.getLogger(__name__)

class RemoteActions:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo

    def remote_list(self):
        remotes = self.repo.remotes
        print("Você também pode configurar as fontes e filtros manualmente editando o arquivo:")
        print(RText.parse(f"[y]{self.repo.paths.config_file}[.]"))
        if len(remotes) == 0:
            print("Nenhuma fonte configurada")
            return
        print("Fontes configuradas:")
        for remote in remotes:
            self.show_source(remote)
    
    def show_source(self, remote: Remote):
        print(RText.parse(f"- Rótulo: [y]{remote.data.name}[.]"))
        print(RText.parse(f"  - Link ou Caminho: [y]{remote.data.target}[.]"))
        print(RText.parse(f"  - Index          : [y]{remote.data.index}[.]"))
        print(RText.parse(f"  - Filtro Quests  : [y]{'Desativado' if remote.data.quest_filters is None else 'Ativado'}[.]"))
        if remote.data.quest_filters is not None:
            for f, v in remote.data.quest_filters.items():
                print(f"    - {f}: {v}")

    def remote_rm(self, alias: str) -> None:
        found = False
        for remote in self.repo.remotes:
            if remote.data.name == alias:
                found = True
                self.repo.data.del_remote(alias)
                print(RText.parse(f"Fonte [y]{alias}[.] removida com sucesso."))
                break
        if not found:
            raise Warning("fail: fonte não encontrada.")
        RepositoryLoader(self.repo).save_config()

    def remote_set(self, alias: str, target: str | None = None, index: str | None = None) -> None:
        repo = self.repo
        remote: Remote | None = repo.data.get_remote(alias)
        if remote is None:
            raise Warning("fail: fonte não encontrada.")
        change: bool = False

        if target is not None:
            remote.data.target = target
            change = True
        if index is not None:
            remote.data.index = index
            change = True
        self.show_source(remote)
        if change:
            print(RText.parse(f"Filtros [y]{alias}[.] atualizados com sucesso."))
            RepositoryLoader(repo).save_config()

    def remote_filter(self, alias: str, filter_quest: list[str] | None = None, clear: bool = False, filter_to: str | None = None) -> None:
        repo = self.repo
        source = repo.data.get_remote(alias)
        if source is None:
            raise Warning("fail: fonte não encontrada.")
        change: bool = False

        if filter_quest is not None:
            if source.data.quest_filters is None:
                source.data.quest_filters = {}
            for f in filter_quest:
                if f not in source.data.quest_filters:
                    change = True
                    source.data.quest_filters[f] = filter_to if filter_to is not None else ""
            
        if clear:
            change = True
            source.data.quest_filters = None
        
        # if not quests and not tasks and not clear:
        self.show_source(source)
        if change:
            print(RText.parse(f"Filtros [y]{alias}[.] atualizados com sucesso."))
            RepositoryLoader(repo).save_config()

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
            index: str | None,
            filter_quest: list[str] | None, 
            filter_task: list[str] | None, 
            filter_to: str | None,
            writeable: bool, branch: str = "main"
            ) -> None:
        
        remotes = self.repo.remotes
        if any(remote.data.name == name for remote in remotes):
            raise Warning("fail: fonte com esse nome já existe.")

        repo = self.repo
        if remote_default is not None:
            print(RText.parse(f"Adicionando fonte remota apontando para repositório git remoto [y]{remote_default}[.]"))
            url: str = ""
            settings = self.settings
            if not settings.has_alias_git(remote_default):
                raise Warning("fail: alias git remoto não encontrado.")
            try:
                url = settings.get_alias_git(remote_default)
                self.git_clone_repository(url)
                remote = Remote(alias=name)
                remote.data.set_git_source(target=url, branch=branch, index=index)
                remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
                self.repo.data.set_remote(remote)
            except Warning:
                logger.exception("Erro ao clonar repositório, fonte não foi adicionada")
                raise Warning("fail: não foi possível clonar o repositório.")
        elif remote_dir is not None:
            dir_path = Path(remote_dir)
            if not dir_path.exists() or not dir_path.is_dir():
                raise Warning("fail: diretório remoto não encontrado.")
            print(RText.parse(f"Adicionando fonte remota apontando parao repositório no diretorio [y]{dir_path}[.]"))
            remote = Remote(alias=name)
            remote.data.set_local_source(target=dir_path)
            remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
            self.repo.data.set_remote(remote)
        elif remote_url is not None:
            print(RText.parse(f"Adicionando fonte remota apontando para repositório git remoto [y]{remote_url}[.]"))
            try:
                self.git_clone_repository(remote_url)
                remote = Remote(alias=name)
                remote.data.set_git_source(target=remote_url, branch=branch, index=index)
                remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
                remote.data.is_editable = writeable
                self.repo.data.set_remote(remote)
                print(RText.parse(f"Fonte remota [y]{name}[.] adicionada com sucesso."))
            except Warning:
                logger.exception("Erro ao clonar repositório, fonte não foi adicionada")
                raise Warning("fail: não foi possível clonar o repositório.")
        RepositoryLoader(repo).save_config()
   
    def git_clone_repository(self, link: str) -> None:
        print(RText.parse(f"Clonando repositório remoto [y]{link}[.]."))
        repo_dir = self.repo.git_cache.get_remote_dir(link, verbose=True)
        if repo_dir is None:
            raise Warning("fail: não foi possível clonar o repositório.")
        print(RText.parse(f"Repositório [y]{link}[.] clonado com sucesso."))
        


    def print_end_msg(self):
        print(RText.parse(f"Voce pode acessar o repositório com o comando [g]tko open[.]"))
        
