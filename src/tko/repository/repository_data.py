from __future__ import annotations
from dataclasses import dataclass, replace
from loguru import logger
from tko.i18n import Msg
from tko.repository.remote import Source
from tko.repository.remote_resolver import SourceResolver
from tko.repository.git_cache import GitCache
from typing import cast
from pathlib import Path

type ConfigValue = str | int | bool | None | list[ConfigValue] | dict[str, ConfigValue]
type ConfigDict = dict[str, ConfigValue]


_REPOSITORY_DATA_LOAD_ERROR = Msg.text(
    pt="Erro ao carregar dados do dicionário",
    en="Error loading data from dictionary",
)
_AUTHORING_SOURCE_NOT_CONFIGURED = Msg.text(
    pt="Fonte de autoria não configurada",
    en="Authoring source is not configured",
)
_SOURCE_NOT_FOUND = Msg.text(
    pt="Fonte '{label}' não encontrada",
    en="Source '{label}' was not found",
)
_SOURCE_EXTERNAL_AUTHORING = Msg.text(
    pt="Fonte '{label}' é externa e não pode ser usada para autoria",
    en="Source '{label}' is external and cannot be used for authoring",
)
_SOURCE_POINTS_OUTSIDE_WORKSPACE = Msg.text(
    pt="Fonte '{label}' aponta para fora do workspace",
    en="Source '{label}' points outside the workspace",
)
_AUTHORING_SOURCE_NOT_EDITABLE = Msg.text(
    pt="Fonte de autoria '{label}' não possui índice editável",
    en="Authoring source '{label}' index is not editable",
)
_AUTHORING_SOURCE_FOLDER_BLOCKED = Msg.text(
    pt="A pasta da fonte de autoria '{label}' não pode ser criada",
    en="Authoring source '{label}' activity folder cannot be created",
)


@dataclass
class AuditConfig:
    enabled: bool = False
    interval_seconds: int | None = None

    def from_dict(self, data: ConfigDict) -> AuditConfig:
        enabled = data.get("enabled")
        if isinstance(enabled, bool):
            self.enabled = enabled

        interval_seconds = data.get("interval_seconds")
        if isinstance(interval_seconds, int):
            self.interval_seconds = interval_seconds
        elif interval_seconds is None:
            self.interval_seconds = None

        return self

    def to_dict(self) -> ConfigDict:
        return {
            "enabled": self.enabled,
            "interval_seconds": self.interval_seconds,
        }


@dataclass
class ProfileLink:
    uri: str = ""
    refresh_minutes: int = 60
    updated_at: str = ""
    revision: str = ""
    content_hash: str = ""

    def from_dict(self, data: ConfigDict) -> ProfileLink:
        uri = data.get("uri")
        if isinstance(uri, str):
            self.uri = uri
        refresh_minutes = data.get("refresh_minutes")
        if isinstance(refresh_minutes, int):
            self.refresh_minutes = refresh_minutes
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            self.updated_at = updated_at
        revision = data.get("revision")
        if isinstance(revision, str):
            self.revision = revision
        content_hash = data.get("content_hash")
        if isinstance(content_hash, str):
            self.content_hash = content_hash
        return self

    def to_dict(self) -> ConfigDict:
        output: ConfigDict = {
            "uri": self.uri,
            "refresh_minutes": self.refresh_minutes,
            "updated_at": self.updated_at,
        }
        if self.revision:
            output["revision"] = self.revision
        if self.content_hash:
            output["content_hash"] = self.content_hash
        return output

class RepositoryData:
    def __init__(self, root_folder: Path):
        self.root_folder: Path = root_folder
        self.version: str = ""
        self.authoring_source: str = "labs"
        self.__sources: dict[str, Source] = {}
        self.set_source(Source.from_local_file("labs", Path("README.md"), is_editable=True))
        self.expanded: list[str] = []
        self.flags: ConfigDict = {}
        self.audit: AuditConfig = AuditConfig()
        self.lang: str = ""
        self.profile_language: str = ""
        self.profile_name: str = ""
        self.link: ProfileLink | None = None
        self.selected: str = ""
        self.selected_index: int = 0

    @property
    def is_linked(self) -> bool:
        return self.link is not None and bool(self.link.uri)

    @property
    def audit_enabled(self) -> bool:
        return self.audit.enabled

    @audit_enabled.setter
    def audit_enabled(self, value: bool) -> None:
        self.audit.enabled = value

    @property
    def audit_interval_seconds(self) -> int | None:
        return self.audit.interval_seconds

    @audit_interval_seconds.setter
    def audit_interval_seconds(self, value: int | None) -> None:
        self.audit.interval_seconds = value

    def set_source(self, source: Source) -> None:
        if source.is_local_source:
            resolver = SourceResolver(GitCache(self.root_folder / ".tko" / "cache"), self.root_folder)
            source = replace(
                source,
                path_or_url=resolver.serialize_uri(source),
                is_editable=resolver.is_editable_index(source),
            )
        self.__sources[source.name] = source

    def get_source(self, name: str) -> Source | None:
        return self.__sources.get(name, None)

    def get_authoring_source(self) -> Source | None:
        return self.get_source(self.authoring_source)

    def get_authoring_source_throw(self) -> Source:
        source = self.get_authoring_source()
        if source is None:
            raise ValueError(str(_SOURCE_NOT_FOUND).format(label=self.authoring_source))
        return source

    def get_sources(self) -> dict[str, Source]:
        return dict(self.__sources)

    def remove_source(self, label: str) -> bool:
        if label == self.authoring_source:
            raise ValueError(f"Source '{label}' is the authoring source\nSelect another authoring source before removing it")
        if label in self.__sources:
            del self.__sources[label]
            return True
        return False

    def set_authoring_source(self, label: str) -> None:
        previous = self.authoring_source
        self.authoring_source = label
        try:
            self.validate_authoring_source()
        except ValueError:
            self.authoring_source = previous
            raise

    def _load_str(self, data: ConfigDict, key: str, default_value: str) -> str:
        value = data.get(key)
        return value if isinstance(value, str) else default_value

    def _load_int(self, data: ConfigDict, key: str, default_value: int) -> int:
        value = data.get(key)
        return value if isinstance(value, int) else default_value

    def _load_list(self, data: ConfigDict, key: str, default_value: list[str]) -> list[str]:
        value = data.get(key)
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return cast(list[str], value)
        return default_value

    def _load_dict(self, data: ConfigDict, key: str) -> ConfigDict | None:
        value = data.get(key)
        if isinstance(value, dict):
            return value
        return None

    def _load_sources_map(self, sources_data: ConfigDict) -> None:
        self.__sources.clear()
        for label, source_data in sources_data.items():
            if not isinstance(source_data, dict):
                continue
            uri = source_data.get("uri")
            if isinstance(uri, str):
                self.set_source(Source.from_uri(label, uri))

    def _load_sources_list(self, sources_data: list[ConfigDict]) -> None:
        self.__sources.clear()
        for item in sources_data:
            source = Source.from_dict(item)
            self.set_source(source)

    def _load_source_list(self, data: ConfigDict, key: str) -> list[ConfigDict] | None:
        value = data.get(key)
        if not isinstance(value, list):
            return None
        sources: list[ConfigDict] = []
        for item in value:
            if isinstance(item, dict):
                sources.append(item)
        return sources

    def _load_profile_from_dict(self, profile: ConfigDict) -> None:
        self.profile_name = self._load_str(profile, "name", "")
        authoring_source = self._load_str(profile, "authoring_source", self.authoring_source)
        self.profile_language = self._load_str(profile, "language", "")
        if self.profile_language:
            self.lang = self.profile_language
        sources = self._load_dict(profile, "sources")
        if sources is not None:
            self._load_sources_map(sources)
        self.authoring_source = authoring_source
        audit_data = self._load_dict(profile, "audit")
        if audit_data is not None:
            _ = self.audit.from_dict(audit_data)
        else:
            self.audit = AuditConfig()

    def validate_authoring_source(self) -> None:
        if not self.authoring_source:
            raise ValueError(str(_AUTHORING_SOURCE_NOT_CONFIGURED))
        source = self.get_source(self.authoring_source)
        if source is None:
            raise ValueError(str(_SOURCE_NOT_FOUND).format(label=self.authoring_source))
        resolver = SourceResolver(GitCache(self.root_folder / ".tko" / "cache"), self.root_folder)
        if not resolver.is_local_internal(source):
            if source.is_git_source:
                raise ValueError(str(_SOURCE_EXTERNAL_AUTHORING).format(label=self.authoring_source))
            raise ValueError(str(_SOURCE_POINTS_OUTSIDE_WORKSPACE).format(label=self.authoring_source))
        if not resolver.is_editable_index(source):
            raise ValueError(str(_AUTHORING_SOURCE_NOT_EDITABLE).format(label=self.authoring_source))
        activity_dir = resolver.source_activity_dir(source)
        if activity_dir.exists() and not activity_dir.is_dir():
            raise ValueError(str(_AUTHORING_SOURCE_FOLDER_BLOCKED).format(label=self.authoring_source))

    def update_profile_from_dict(self, profile: ConfigDict) -> None:
        self._load_profile_from_dict(profile)
        self.validate_authoring_source()

    def load_from_dict(self, data: ConfigDict) -> None:
        try:
            # Load simple fields
            self.version = self._load_str(data, "version", self.version)
            link = self._load_dict(data, "link")
            self.link = ProfileLink().from_dict(link) if link is not None else None
            profile = self._load_dict(data, "profile")
            if profile is not None:
                self._load_profile_from_dict(profile)

            preferences = self._load_dict(data, "preferences")
            if preferences is not None:
                if not self.profile_language:
                    self.lang = self._load_str(preferences, "lang", self.lang)
                self.flags = {key: value for key, value in preferences.items() if key != "lang"}
            else:
                flags = self._load_dict(data, "flags")
                if flags is not None:
                    self.flags = flags
                if not self.profile_language:
                    self.lang = self._load_str(data, "lang", self.lang)

            state = self._load_dict(data, "state")
            if state is not None:
                self.expanded = self._load_list(state, "expanded", self.expanded)
                self.selected = self._load_str(state, "selected", self.selected)
                self.selected_index = self._load_int(state, "selected_index", self.selected_index)
            else:
                self.expanded = self._load_list(data, "expanded", self.expanded)
                self.selected = self._load_str(data, "selected", self.selected)
                self.selected_index = self._load_int(data, "selected_index", self.selected_index)

            sandbox_name = data.get("sandbox_name")
            sandbox_index = data.get("sandbox_index")
            if sandbox_name is not None:
                if profile is None:
                    self.__sources.clear()
                if isinstance(sandbox_name, str):
                    self.authoring_source = sandbox_name
                if isinstance(sandbox_name, str) and isinstance(sandbox_index, str):
                    self.set_source(Source.from_uri(sandbox_name, sandbox_index, is_editable=True))

            audit_data = self._load_dict(data, "audit")
            if audit_data is not None:
                _ = self.audit.from_dict(audit_data)

            # Load the 'source' field with specific validation
            source_data = self._load_source_list(data, "sources")
            if source_data is not None:
                existing_authoring = self.get_source(self.authoring_source)
                self._load_sources_list(source_data)
                if existing_authoring is not None:
                    self.set_source(existing_authoring)
            elif "sources" in data:
                raise TypeError("The 'sources' field must be a list.")
            self.validate_authoring_source()

        except (KeyError, TypeError):
            logger.exception(str(_REPOSITORY_DATA_LOAD_ERROR))

    def to_dict(self) -> ConfigDict:
        resolver = SourceResolver(GitCache(self.root_folder / ".tko" / "cache"), self.root_folder)
        sources: ConfigDict = {
            remote.name: {"uri": resolver.serialize_uri(remote)}
            for remote in self.__sources.values()
        }
        profile: ConfigDict = {
            "authoring_source": self.authoring_source,
            "sources": sources,
            "audit": self.audit.to_dict(),
        }
        if self.profile_name:
            profile["name"] = self.profile_name
        if self.profile_language:
            profile["language"] = self.profile_language
        preferences: ConfigDict = self.flags.copy()
        if self.lang and not self.profile_language:
            preferences["lang"] = self.lang
        state: ConfigDict = {
            "expanded": list(self.expanded),
            "selected": self.selected,
            "selected_index": self.selected_index,
        }
        output: ConfigDict = {
            "version": self.version,
            "profile": profile,
            "preferences": preferences,
            "state": state,
        }
        if self.link is not None:
            output["link"] = self.link.to_dict()
        return output
