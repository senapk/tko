from loguru import logger
from tko.repository.remote import Remote
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.repository.repository_config import RepositoryLoader
from tko.util.console import Console
from tko.util.git_hub_url import GitHubUrl
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
_REMOTE_EDITABLE = Msg.parse(pt="[y]- Editável: {index}", 
                    en="[y]- Editable: {index}")
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
_REMOTE_FILE_NOT_FOUND = Msg.text(
    pt="fail: arquivo remoto não encontrado.",
    en="fail: remote file not found.",
)
_REMOTE_ADDING_LOCAL = Msg.text(
    pt="Adicionando fonte remota apontando para a fonte remota {path}",
    en="Adding remote source pointing to remote source {path}",
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
        for remote in remotes.values():
            self.show_source(remote)
    
    def show_source(self, remote: Remote):
        Console.print(_REMOTE_LABEL.t().format(name=remote.name))
        Console.print(_REMOTE_LINK.t().format(link=remote.path_or_url))
        Console.print(_REMOTE_EDITABLE.t().format(index=remote.is_editable))

    def remote_rm(self, alias: str) -> bool:
        if alias in self.repo.remotes:
            del self.repo.remotes[alias]
            logger.info(str(_REMOTE_REMOVED_SUCCESS).format(alias=alias))
            RepositoryLoader(self.repo).save()
            return True
        logger.warning(str(_REMOTE_NOT_FOUND).format(alias=alias))
        return False

    def remote_set(self, alias: str, target: str | None = None) -> bool:
        repo = self.repo
        remote: Remote | None = repo.data.get_remote(alias)
        if remote is None:
            logger.warning(_REMOTE_NOT_FOUND.t().format(alias=alias))
            return False
        if target is not None:
            repo.data.set_remote(Remote(name=alias, path_or_url=target, source_type=remote.source_type, is_editable=remote.is_editable))
        self.show_source(remote)
        return True

    def fix_filter(self, source: list[str] | None, destiny: str | None) -> dict[str, str] | None:
        if source is None:
            return None
        return {s: destiny if destiny is not None else "" for s in source}

    def remote_add( self, name: str, target: str, writeable: bool = False ) -> bool:
        default_git_alias = target[1:] if target.startswith("@") else None
        git_repository_url = target if target.startswith(("http:", "https:")) else None
        local_source_file = target if not (default_git_alias or git_repository_url) else None
        ok = self.remote_add_splitted(
            name=name,
            remote_default=default_git_alias,
            remote_url=git_repository_url,
            remote_file=local_source_file,
            writeable=writeable,
            )
        if ok:
            RepositoryLoader(self.repo).save()

    def remote_add_splitted( self, name: str, remote_default: str | None, remote_file: str | None, remote_url: str | None, writeable: bool = False ) -> bool:
        remotes = self.repo.remotes
        if any(remote.name == name for remote in remotes.values()):
            logger.warning(str(_REMOTE_NAME_EXISTS))
            return False
        if remote_default is not None:
            Console.print(RT.parse(f"[y] {_REMOTE_ADDING_GIT.t().format(url=remote_default)}"))
            url: str | None = None
            settings = self.settings
            if not settings.has_alias_git(remote_default):
                raise Warning(_REMOTE_GIT_ALIAS_NOT_FOUND.t())
            url = settings.get_alias_git(remote_default)
            if url is None:
                logger.warning(_REMOTE_GIT_ALIAS_NOT_FOUND.t())
                return False
            return self.add_from_url(name=name, url=url)
            
        elif remote_file is not None:
            remote_file_path = Path(remote_file).expanduser().resolve()
            if not remote_file_path.exists() or not remote_file_path.is_dir():
                logger.warning(str(_REMOTE_FILE_NOT_FOUND))
                return False
            Console.print(RT.parse(f"[y] {str(_REMOTE_ADDING_LOCAL).format(path=remote_file_path)}"))
            remote = Remote.from_local_file(name=name, target=remote_file_path, is_editable=writeable)
            self.repo.data.set_remote(remote)
            return True

        elif remote_url is not None:
            Console.print(RT.parse(f"[y] {_REMOTE_ADDING_URL.t().format(url=remote_url)}"))
            return self.add_from_url(name=name, url=remote_url)
        return False
        
    def add_from_url(self, name: str, url: GitHubUrl | str) -> bool:
        if isinstance(url, str):
            ghur = GitHubUrl.parse(url)
            if ghur is None:
                logger.warning(str(_REMOTE_CLONE_FAILED))
                return False
            url = ghur
        ok = self.git_clone_repository(url)
        if not ok:
            return False
        file, ok = self.repo.git_cache.git_hub_url_to_path(url, load_git=True)
        if not ok:
            return False
        if not file.exists():
            logger.warning(str(_REMOTE_FILE_NOT_FOUND))
            return False
        remote = Remote.from_git_file(name=name, target=url.repository_url)
        if remote is None:
            logger.warning(str(_REMOTE_CLONE_FAILED))
            return False
        self.repo.data.set_remote(remote)
        Console.print(RT.parse(f"[y] {str(_REMOTE_ADDED_SUCCESS).format(name=name)}"))
        return True

    def git_clone_repository(self, link: str | GitHubUrl) -> bool:
        if isinstance(link, str):
            ghu = GitHubUrl.parse(link)
            if ghu is None:
                logger.warning(str(_REMOTE_CLONE_FAILED))
                return False
            else:
                link = ghu

        Console.print(_REMOTE_CLONING.t().format(link=link))
        _, ok = self.repo.git_cache.get_repository_dir(link.repository_url, load_git=True)
        if ok:
            Console.print(_REMOTE_CLONED_SUCCESS.t().format(link=link))
            logger.info(_REMOTE_CLONED_SUCCESS.t().format(link=link))
        else:
            Console.print(_REMOTE_CLONE_FAILED.t())
            logger.warning(_REMOTE_CLONE_FAILED.t())
        return ok
        


        
