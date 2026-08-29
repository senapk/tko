from __future__ import annotations

from dataclasses import replace
from loguru import logger

from tko.config.settings import Settings
from tko.i18n import Msg
from tko.repository.remote import Remote, SourceType
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader
from tko.util.console import Console
from tko.util.git_hub_url import GitHubUrl
from tko.util.rt import RT


_SOURCE_EDIT_HINT = Msg.text(
    pt="Você também pode configurar as fontes manualmente editando o arquivo:",
    en="You can also configure sources manually by editing the file:",
)
_SOURCE_NONE_CONFIGURED = Msg.text(pt="Nenhuma fonte configurada", en="No sources configured")
_SOURCE_CONFIGURED = Msg.text(pt="Fontes configuradas:", en="Configured sources:")
_SOURCE_HEADER = Msg.text(
    pt="LABEL  CONTEXTO  URI  AUTORIA",
    en="LABEL  CONTEXT  URI  AUTHORING",
)
_SOURCE_ROW = Msg.text(
    pt="{label}  {context}  {uri}  {authoring}",
    en="{label}  {context}  {uri}  {authoring}",
)
_SOURCE_REMOVED_SUCCESS = Msg.text(
    pt="Fonte {label} removida com sucesso.",
    en="Source {label} removed successfully.",
)
_SOURCE_NOT_FOUND = Msg.text(pt="fail: fonte {label} não encontrada.", en="fail: source {label} not found.")
_SOURCE_LABEL_EXISTS = Msg.text(
    pt="fail: fonte com esse rótulo já existe.",
    en="fail: a source with this label already exists.",
)
_SOURCE_GIT_ALIAS_NOT_FOUND = Msg.text(
    pt="fail: alias git não encontrado.",
    en="fail: git alias not found.",
)
_SOURCE_CLONE_FAILED = Msg.text(
    pt="fail: não foi possível acessar o repositório.",
    en="fail: could not access the repository.",
)
_SOURCE_FILE_NOT_FOUND = Msg.text(
    pt="fail: arquivo da fonte não encontrado.",
    en="fail: source file not found.",
)
_SOURCE_ADDED_SUCCESS = Msg.text(
    pt="Fonte {label} adicionada com sucesso.",
    en="Source {label} added successfully.",
)
_SOURCE_UPDATED_SUCCESS = Msg.text(
    pt="Fonte {label} atualizada com sucesso.",
    en="Source {label} updated successfully.",
)
_SOURCE_AUTHORING_SUCCESS = Msg.text(
    pt="Fonte de autoria definida como {label}.",
    en="Authoring source set to {label}.",
)
_SOURCE_ACCESSING_GIT = Msg.text(
    pt="Acessando repositório Git {link}",
    en="Accessing Git repository {link}",
)
_SOURCE_GIT_ACCESSED = Msg.text(
    pt="Repositório {link} acessado com sucesso.",
    en="Repository {link} accessed successfully.",
)


class SourceActions:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo

    def list_sources(self) -> None:
        sources = self.repo.sources
        Console.print(_SOURCE_EDIT_HINT.t())
        Console.print(RT.run("y", self.repo.paths.config_file.as_posix()))
        if not sources:
            Console.print(_SOURCE_NONE_CONFIGURED.t())
            return
        Console.print(_SOURCE_CONFIGURED.t())
        Console.print(_SOURCE_HEADER.t())
        for source in sources.values():
            self.show_source(source)

    def show_source(self, source: Remote) -> None:
        authoring = "yes" if source.name == self.repo.data.authoring_source else "no"
        Console.print(
            _SOURCE_ROW.t().format(
                label=source.name,
                context=self.context_name(source),
                uri=self.repo.remote_resolver.serialize_uri(source),
                authoring=authoring,
            )
        )

    def context_name(self, source: Remote) -> str:
        if source.source_type == SourceType.GIT_SOURCE:
            return "git"
        if self.repo.remote_resolver.is_local_internal(source):
            return "managed"
        return "local"

    def remove_source(self, label: str) -> bool:
        try:
            if self.repo.data.remove_source(label):
                logger.info(str(_SOURCE_REMOVED_SUCCESS).format(label=label))
                RepositoryLoader(self.repo).save()
                return True
        except ValueError as error:
            logger.warning(str(error))
            return False
        logger.warning(str(_SOURCE_NOT_FOUND).format(label=label))
        return False

    def update_source(self, label: str, uri: str | None = None) -> bool:
        source = self.repo.data.get_source(label)
        if source is None:
            logger.warning(_SOURCE_NOT_FOUND.t().format(label=label))
            return False
        if uri is None:
            self.show_source(source)
            return True

        updated = self._source_from_uri(label, uri)
        previous = source
        self.repo.data.set_source(updated)
        try:
            if label == self.repo.data.authoring_source:
                self.repo.data.validate_authoring_source()
        except ValueError as error:
            self.repo.data.set_source(previous)
            logger.warning(str(error))
            return False

        RepositoryLoader(self.repo).save()
        logger.info(str(_SOURCE_UPDATED_SUCCESS).format(label=label))
        return True

    def set_authoring_source(self, label: str) -> bool:
        try:
            self.repo.data.set_authoring_source(label)
        except ValueError as error:
            logger.warning(str(error))
            return False
        RepositoryLoader(self.repo).save()
        logger.info(str(_SOURCE_AUTHORING_SUCCESS).format(label=label))
        return True

    def add_source(self, label: str, uri: str, authoring: bool = False) -> bool:
        if label in self.repo.sources:
            logger.warning(str(_SOURCE_LABEL_EXISTS))
            return False

        previous_authoring = self.repo.data.authoring_source
        source = self._source_from_uri(label, uri)
        self.repo.data.set_source(source)
        try:
            if authoring:
                self.repo.data.set_authoring_source(label)
            RepositoryLoader(self.repo).save()
        except ValueError as error:
            self.repo.data.rm_remote_legacy(label)
            self.repo.data.authoring_source = previous_authoring
            logger.warning(str(error))
            return False

        logger.info(str(_SOURCE_ADDED_SUCCESS).format(label=label))
        return True

    def add_default_source(self, label: str, default_alias: str) -> bool:
        if not self.settings.has_alias_git(default_alias):
            raise Warning(_SOURCE_GIT_ALIAS_NOT_FOUND.t())
        uri = self.settings.get_alias_git(default_alias)
        if uri is None:
            logger.warning(_SOURCE_GIT_ALIAS_NOT_FOUND.t())
            return False
        return self.add_source(label=label, uri=uri)

    def _source_from_uri(self, label: str, uri: str) -> Remote:
        if uri.startswith("@"):
            alias = uri[1:]
            if not self.settings.has_alias_git(alias):
                raise Warning(_SOURCE_GIT_ALIAS_NOT_FOUND.t())
            resolved = self.settings.get_alias_git(alias)
            if resolved is None:
                raise Warning(_SOURCE_GIT_ALIAS_NOT_FOUND.t())
            uri = resolved

        git_url = GitHubUrl.parse(uri)
        if git_url is not None:
            if not self.git_clone_repository(git_url):
                raise ValueError(str(_SOURCE_CLONE_FAILED))
            index_path, ok = self.repo.git_cache.git_hub_url_to_path(git_url, load_git=True)
            if not ok or not index_path.exists():
                raise ValueError(str(_SOURCE_FILE_NOT_FOUND))
            source = Remote.from_git_file(name=label, target=git_url.blob_url)
            if source is None:
                raise ValueError(str(_SOURCE_CLONE_FAILED))
            return source

        source = Remote.from_uri(label, uri)
        resolved_path = self.repo.remote_resolver.resolve_local_uri(source.path_or_url)
        if not self.repo.remote_resolver.is_local_internal(source) and not resolved_path.exists():
            raise ValueError(str(_SOURCE_FILE_NOT_FOUND))
        return replace(source, path_or_url=self.repo.remote_resolver.serialize_uri(source))

    def git_clone_repository(self, link: GitHubUrl) -> bool:
        Console.print(_SOURCE_ACCESSING_GIT.t().format(link=link.repository_url))
        _, ok = self.repo.git_cache.get_repository_dir(link.repository_url, load_git=True)
        if ok:
            Console.print(_SOURCE_GIT_ACCESSED.t().format(link=link.repository_url))
            logger.info(_SOURCE_GIT_ACCESSED.t().format(link=link.repository_url))
        else:
            Console.print(_SOURCE_CLONE_FAILED.t())
            logger.warning(_SOURCE_CLONE_FAILED.t())
        return ok
