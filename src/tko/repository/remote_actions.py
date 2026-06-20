from loguru import logger
from tko.repository.remote import Remote
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.repository.repository_config import RepositoryConfig
from tko.util.console import Console
from tko.util.rt import RT
from tko.i18n import Msg
from pathlib import Path

_REMOTE_EDIT_HINT = Msg.text(
    pt="Você também pode configurar as fontes e filtros manualmente editando o arquivo:",
    en="You can also configure sources and filters manually by editing the file:",
)
_REMOTE_NONE_CONFIGURED = Msg.text(pt="Nenhuma fonte configurada", en="No sources configured")
_REMOTE_CONFIGURED_SOURCES = Msg.text(pt="Fontes configuradas:", en="Configured sources:")
_REMOTE_LABEL = Msg.parse(pt="[y]- Rótulo: {name}", 
                    en="[y]- Label: {name}")
_REMOTE_LINK = Msg.parse(pt="[y]- Link ou Caminho: {link}", 
                   en="[y]- Link or Path: {link}")
_REMOTE_INDEX = Msg.parse(pt="[y]- Índice: {index}", 
                    en="[y]- Index: {index}")
_REMOTE_QUEST_FILTER = Msg.parse(pt="[y]- Filtro Quests: {status}", 
                           en="[y]- Quest Filter: {status}")
_REMOTE_FILTER_DISABLED = Msg.text(pt="Desativado", en="Disabled")
_REMOTE_FILTER_ENABLED = Msg.text(pt="Ativado", en="Enabled")

_REMOTE_REMOVED_SUCCESS = Msg.text(
    pt="Fonte {alias} removida com sucesso.",
    en="Source {alias} removed successfully.",
)
_REMOTE_NOT_FOUND = Msg.text(pt="fail: fonte {alias} não encontrada.", en="fail: source {alias} not found.")
_REMOTE_FILTERS_UPDATED = Msg.text(
    pt="Filtros {alias} atualizados com sucesso.",
    en="Filters for {alias} updated successfully.",
)
_REMOTE_NAME_EXISTS = Msg.text(
    pt="fail: fonte com esse nome já existe.",
    en="fail: a source with this name already exists.",
)
_REMOTE_ADDING_GIT = Msg.text(
    pt="Adicionando fonte remota apontando para repositório git remoto {url}",
    en="Adding remote source pointing to git repository {url}",
)
_REMOTE_GIT_ALIAS_NOT_FOUND = Msg.text(
    pt="fail: alias git remoto não encontrado.",
    en="fail: remote git alias not found.",
)
_REMOTE_CLONE_ERROR = Msg.text(
    pt="Erro ao acessar repositório, fonte não foi adicionada",
    en="Error accessing repository, source was not added",
)
_REMOTE_CLONE_FAILED = Msg.text(
    pt="fail: não foi possível acessar o repositório.",
    en="fail: could not access the repository.",
)
_REMOTE_DIR_NOT_FOUND = Msg.text(
    pt="fail: diretório remoto não encontrado.",
    en="fail: remote directory not found.",
)
_REMOTE_ADDING_LOCAL = Msg.text(
    pt="Adicionando fonte remota apontando para o repositório no diretório {path}",
    en="Adding remote source pointing to repository in directory {path}",
)
_REMOTE_ADDING_URL = Msg.text(
    pt="Adicionando fonte remota apontando para repositório git remoto {url}",
    en="Adding remote source pointing to git repository {url}",
)
_REMOTE_ADDED_SUCCESS = Msg.text(
    pt="Fonte remota {name} adicionada com sucesso.",
    en="Remote source {name} added successfully.",
)
_REMOTE_CLONING = Msg.text(
    pt="Acessando repositório remoto {link}",
    en="Accessing remote repository {link}",
)
_REMOTE_CLONED_SUCCESS = Msg.text(
    pt="Repositório {link} acessado com sucesso.",
    en="Repository {link} accessed successfully.",
)

class RemoteActions:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo

    def remote_list(self):
        remotes = self.repo.remotes
        Console.print(_REMOTE_EDIT_HINT.t())
        Console.print(RT.run("y", self.repo.paths.config_file.as_posix()))
        if len(remotes) == 0:
            Console.print(_REMOTE_NONE_CONFIGURED.t())
            return
        Console.print(_REMOTE_CONFIGURED_SOURCES.t())
        for remote in remotes:
            self.show_source(remote)
    
    def show_source(self, remote: Remote):
        status = str(_REMOTE_FILTER_DISABLED) if remote.data.quest_filters is None else str(_REMOTE_FILTER_ENABLED)
        Console.print(_REMOTE_LABEL.t().format(name=remote.data.name))
        Console.print(_REMOTE_LINK.t().format(link=remote.data.target))
        Console.print(_REMOTE_INDEX.t().format(index=remote.data.index))
        Console.print(_REMOTE_QUEST_FILTER.t().format(status=status))
        if remote.data.quest_filters is not None:
            for f, v in remote.data.quest_filters.items():
                Console.print(f"    - {f}: {v}")

    def remote_rm(self, alias: str) -> bool:
        if self.repo.data.del_remote(alias):
            logger.info(str(_REMOTE_REMOVED_SUCCESS).format(alias=alias))
            RepositoryConfig(self.repo).save()
            return True
        logger.warning(str(_REMOTE_NOT_FOUND).format(alias=alias))
        return False

    def remote_set(self, alias: str, target: str | None = None, index: str | None = None) -> bool:
        repo = self.repo
        remote: Remote | None = repo.data.get_remote(alias)
        if remote is None:
            logger.warning(str(_REMOTE_NOT_FOUND).format(alias=alias))
            return False
        change: bool = False

        if target is not None:
            remote.data.target = target
            change = True
        if index is not None:
            remote.data.index = index
            change = True
        self.show_source(remote)
        if change:
            logger.info(str(f" {str(_REMOTE_FILTERS_UPDATED).format(alias=alias)}"))
            RepositoryConfig(repo).save()
        return True

    def remote_filter(self, alias: str, filter_quest: list[str] | None = None, clear: bool = False, filter_to: str | None = None) -> bool:
        repo = self.repo
        source = repo.data.get_remote(alias)
        if source is None:
            logger.warning(str(_REMOTE_NOT_FOUND), alias=alias)
            return False
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
            logger.info(f" {str(_REMOTE_FILTERS_UPDATED).format(alias=alias)}")
            RepositoryConfig(repo).save()
        return True

    def fix_filter(self, source: list[str] | None, destiny: str | None) -> dict[str, str] | None:
        if source is None:
            return None
        return {s: destiny if destiny is not None else "" for s in source}

    def remote_add(
            self, 
            name: str, 
            remote_default: str | None = None, 
            remote_url: str | None = None, 
            remote_dir: str | None = None, 
            index: str | None = None,
            filter_quest: list[str] | None = None, 
            filter_to: str | None = None,
            writeable: bool = False, 
            branch: str | None = None
            ) -> bool:
        
        remotes = self.repo.remotes
        if any(remote.data.name == name for remote in remotes):
            logger.warning(str(_REMOTE_NAME_EXISTS))
            return False

        repo = self.repo
        if remote_default is not None:
            Console.print(RT.parse(f"[y] {str(_REMOTE_ADDING_GIT).format(url=remote_default)}"))
            url: str = ""
            settings = self.settings
            if not settings.has_alias_git(remote_default):
                raise Warning(str(_REMOTE_GIT_ALIAS_NOT_FOUND))
            try:
                url = settings.get_alias_git(remote_default)
                self.git_clone_repository(url)
                remote = Remote(alias=name)
                remote.data.set_git_source(target=url, branch=branch, index=index)
                remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
                self.repo.data.set_remote(remote)
            except Warning:
                logger.exception(str(_REMOTE_CLONE_ERROR))
                raise Warning(str(_REMOTE_CLONE_FAILED))
        elif remote_dir is not None:
            dir_path = Path(remote_dir)
            if not dir_path.exists() or not dir_path.is_dir():
                logger.warning(str(_REMOTE_DIR_NOT_FOUND))
                return False
            Console.print(RT.parse(f"[y] {str(_REMOTE_ADDING_LOCAL).format(path=dir_path)}"))
            remote = Remote(alias=name)
            remote.data.set_local_source(target=dir_path)
            remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
            self.repo.data.set_remote(remote)
        elif remote_url is not None:
            Console.print(RT.parse(f"[y] {str(_REMOTE_ADDING_URL).format(url=remote_url)}"))
            try:
                self.git_clone_repository(remote_url)
                remote = Remote(alias=name)
                remote.data.set_git_source(target=remote_url, branch=branch, index=index)
                remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
                remote.data.is_editable = writeable
                self.repo.data.set_remote(remote)
                Console.print(RT.parse(f"[y] {str(_REMOTE_ADDED_SUCCESS).format(name=name)}"))
            except Warning:
                logger.exception(str(_REMOTE_CLONE_ERROR))
                raise Warning(str(_REMOTE_CLONE_FAILED))
        RepositoryConfig(repo).save()
        return True
    
    def git_clone_repository(self, link: str) -> None:
        Console.print(str(_REMOTE_CLONING).format(link=link))
        repo_dir = self.repo.git_cache.get_remote_dir(link)
        if repo_dir is None:
            raise Warning(str(_REMOTE_CLONE_FAILED))
        Console.print(str(_REMOTE_CLONED_SUCCESS).format(link=link))
        


        
