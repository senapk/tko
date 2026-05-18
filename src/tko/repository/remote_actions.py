import logging
from tko.repository.remote import Remote
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.repository.repository_loader import RepositoryLoader
from tko.util.rtext import RText
from tko.i18n import Msg, t
from pathlib import Path


logger = logging.getLogger(__name__)

_REMOTE_EDIT_HINT = Msg(
    pt="Você também pode configurar as fontes e filtros manualmente editando o arquivo:",
    en="You can also configure sources and filters manually by editing the file:",
)
_REMOTE_NONE_CONFIGURED = Msg(pt="Nenhuma fonte configurada", en="No sources configured")
_REMOTE_CONFIGURED_SOURCES = Msg(pt="Fontes configuradas:", en="Configured sources:")
_REMOTE_LABEL = Msg(pt="- Rótulo:", en="- Label:")
_REMOTE_LINK = Msg(pt="- Link ou Caminho:", en="- Link or Path:")
_REMOTE_INDEX = Msg(pt="- Índice:", en="- Index:")
_REMOTE_FILTER_DISABLED = Msg(pt="Desativado", en="Disabled")
_REMOTE_FILTER_ENABLED = Msg(pt="Ativado", en="Enabled")
_REMOTE_QUEST_FILTER = Msg(pt="- Filtro Quests:", en="- Quest Filter:")
_REMOTE_REMOVED_SUCCESS = Msg(
    pt="Fonte {alias} removida com sucesso.",
    en="Source {alias} removed successfully.",
)
_REMOTE_NOT_FOUND = Msg(pt="fail: fonte não encontrada.", en="fail: source not found.")
_REMOTE_FILTERS_UPDATED = Msg(
    pt="Filtros {alias} atualizados com sucesso.",
    en="Filters for {alias} updated successfully.",
)
_REMOTE_NAME_EXISTS = Msg(
    pt="fail: fonte com esse nome já existe.",
    en="fail: a source with this name already exists.",
)
_REMOTE_ADDING_GIT = Msg(
    pt="Adicionando fonte remota apontando para repositório git remoto {url}",
    en="Adding remote source pointing to git repository {url}",
)
_REMOTE_GIT_ALIAS_NOT_FOUND = Msg(
    pt="fail: alias git remoto não encontrado.",
    en="fail: remote git alias not found.",
)
_REMOTE_CLONE_ERROR = Msg(
    pt="Erro ao clonar repositório, fonte não foi adicionada",
    en="Error cloning repository, source was not added",
)
_REMOTE_CLONE_FAILED = Msg(
    pt="fail: não foi possível clonar o repositório.",
    en="fail: could not clone the repository.",
)
_REMOTE_DIR_NOT_FOUND = Msg(
    pt="fail: diretório remoto não encontrado.",
    en="fail: remote directory not found.",
)
_REMOTE_ADDING_LOCAL = Msg(
    pt="Adicionando fonte remota apontando para o repositório no diretório {path}",
    en="Adding remote source pointing to repository in directory {path}",
)
_REMOTE_ADDING_URL = Msg(
    pt="Adicionando fonte remota apontando para repositório git remoto {url}",
    en="Adding remote source pointing to git repository {url}",
)
_REMOTE_ADDED_SUCCESS = Msg(
    pt="Fonte remota {name} adicionada com sucesso.",
    en="Remote source {name} added successfully.",
)
_REMOTE_CLONING = Msg(
    pt="Clonando repositório remoto {link}",
    en="Cloning remote repository {link}",
)
_REMOTE_CLONED_SUCCESS = Msg(
    pt="Repositório {link} clonado com sucesso.",
    en="Repository {link} cloned successfully.",
)
_REMOTE_CAN_ACCESS = Msg(
    pt="Você pode acessar o repositório com o comando [g]tko open[.]",
    en="You can access the repository with the command [g]tko open[.]",
)

class RemoteActions:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo

    def remote_list(self):
        remotes = self.repo.remotes
        print(t(_REMOTE_EDIT_HINT))
        print(RText.parse(f"[y]{self.repo.paths.config_file}[.]"))
        if len(remotes) == 0:
            print(t(_REMOTE_NONE_CONFIGURED))
            return
        print(t(_REMOTE_CONFIGURED_SOURCES))
        for remote in remotes:
            self.show_source(remote)
    
    def show_source(self, remote: Remote):
        print(RText.parse(f"[y]{t(_REMOTE_LABEL)} {remote.data.name}[.]"))
        print(RText.parse(f"  [y]{t(_REMOTE_LINK)} {remote.data.target}[.]"))
        print(RText.parse(f"  [y]{t(_REMOTE_INDEX)} {remote.data.index}[.]"))
        status = t(_REMOTE_FILTER_DISABLED) if remote.data.quest_filters is None else t(_REMOTE_FILTER_ENABLED)
        print(RText.parse(f"  [y]{t(_REMOTE_QUEST_FILTER)} {status}[.]"))
        if remote.data.quest_filters is not None:
            for f, v in remote.data.quest_filters.items():
                print(f"    - {f}: {v}")

    def remote_rm(self, alias: str) -> None:
        found = False
        for remote in self.repo.remotes:
            if remote.data.name == alias:
                found = True
                self.repo.data.del_remote(alias)
                print(RText.parse(f"[y]{t(_REMOTE_REMOVED_SUCCESS, alias=alias)}[.]"))
                break
        if not found:
            raise Warning(t(_REMOTE_NOT_FOUND))
        RepositoryLoader(self.repo).save_config()

    def remote_set(self, alias: str, target: str | None = None, index: str | None = None) -> None:
        repo = self.repo
        remote: Remote | None = repo.data.get_remote(alias)
        if remote is None:
            raise Warning(t(_REMOTE_NOT_FOUND))
        change: bool = False

        if target is not None:
            remote.data.target = target
            change = True
        if index is not None:
            remote.data.index = index
            change = True
        self.show_source(remote)
        if change:
            print(RText.parse(f"[y]{t(_REMOTE_FILTERS_UPDATED, alias=alias)}[.]"))
            RepositoryLoader(repo).save_config()

    def remote_filter(self, alias: str, filter_quest: list[str] | None = None, clear: bool = False, filter_to: str | None = None) -> None:
        repo = self.repo
        source = repo.data.get_remote(alias)
        if source is None:
            raise Warning(t(_REMOTE_NOT_FOUND))
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
            print(RText.parse(f"[y]{t(_REMOTE_FILTERS_UPDATED, alias=alias)}[.]"))
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
            raise Warning(t(_REMOTE_NAME_EXISTS))

        repo = self.repo
        if remote_default is not None:
            print(RText.parse(f"[y]{t(_REMOTE_ADDING_GIT, url=remote_default)}[.]"))
            url: str = ""
            settings = self.settings
            if not settings.has_alias_git(remote_default):
                raise Warning(t(_REMOTE_GIT_ALIAS_NOT_FOUND))
            try:
                url = settings.get_alias_git(remote_default)
                self.git_clone_repository(url)
                remote = Remote(alias=name)
                remote.data.set_git_source(target=url, branch=branch, index=index)
                remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
                self.repo.data.set_remote(remote)
            except Warning:
                logger.exception(t(_REMOTE_CLONE_ERROR))
                raise Warning(t(_REMOTE_CLONE_FAILED))
        elif remote_dir is not None:
            dir_path = Path(remote_dir)
            if not dir_path.exists() or not dir_path.is_dir():
                raise Warning(t(_REMOTE_DIR_NOT_FOUND))
            print(RText.parse(f"[y]{t(_REMOTE_ADDING_LOCAL, path=dir_path)}[.]"))
            remote = Remote(alias=name)
            remote.data.set_local_source(target=dir_path)
            remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
            self.repo.data.set_remote(remote)
        elif remote_url is not None:
            print(RText.parse(f"[y]{t(_REMOTE_ADDING_URL, url=remote_url)}[.]"))
            try:
                self.git_clone_repository(remote_url)
                remote = Remote(alias=name)
                remote.data.set_git_source(target=remote_url, branch=branch, index=index)
                remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
                remote.data.is_editable = writeable
                self.repo.data.set_remote(remote)
                print(RText.parse(f"[y]{t(_REMOTE_ADDED_SUCCESS, name=name)}[.]"))
            except Warning:
                logger.exception(t(_REMOTE_CLONE_ERROR))
                raise Warning(t(_REMOTE_CLONE_FAILED))
        RepositoryLoader(repo).save_config()
   
    def git_clone_repository(self, link: str) -> None:
        print(RText.parse(f"[y]{t(_REMOTE_CLONING, link=link)}[.]"))
        repo_dir = self.repo.git_cache.get_remote_dir(link, verbose=True)
        if repo_dir is None:
            raise Warning(t(_REMOTE_CLONE_FAILED))
        print(RText.parse(f"[y]{t(_REMOTE_CLONED_SUCCESS, link=link)}[.]\n"))
        


    def print_end_msg(self):
        print(RText.parse(f"[y]{t(_REMOTE_CAN_ACCESS)}[.]\n"))
        
