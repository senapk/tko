from __future__ import annotations
from dataclasses import dataclass, replace
from loguru import logger
from tko.i18n import Msg
from tko.repository.remote import Remote
from tko.repository.remote_resolver import RemoteResolver
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

class RepositoryData:
    def __init__(self, root_folder: Path):
        self.root_folder: Path = root_folder
        self.version: str = ""
        self.authoring_source: str = "labs"
        self.__remotes: dict[str, Remote] = {}
        self.set_remote(Remote.from_local_file("labs", Path("README.md"), is_editable=True))
        self.expanded: list[str] = []
        self.flags: ConfigDict = {}
        self.audit: AuditConfig = AuditConfig()
        self.lang: str = ""
        self.selected: str = ""
        self.selected_index: int = 0

    @property
    def sandbox_name(self) -> str:
        return self.authoring_source

    @sandbox_name.setter
    def sandbox_name(self, value: str) -> None:
        old_remote = self.get_authoring_remote()
        self.authoring_source = value
        if old_remote is not None and value not in self.__remotes:
            self.set_remote(Remote(name=value, path_or_url=old_remote.path_or_url, source_type=old_remote.source_type, is_editable=old_remote.is_editable))

    @property
    def sandbox_index(self) -> str:
        remote = self.get_authoring_remote()
        return remote.path_or_url if remote is not None else "README.md"

    @sandbox_index.setter
    def sandbox_index(self, value: str) -> None:
        self.set_remote(Remote.from_uri(self.authoring_source, value, is_editable=True))

    @property
    def sandbox_index_file(self) -> Path:
        return RemoteResolver(GitCache(self.root_folder / ".tko" / "cache"), self.root_folder).resolve_local_uri(self.sandbox_index)

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

    def set_remote(self, remote: Remote) -> None:
        self.set_source(remote)

    def set_source(self, remote: Remote) -> None:
        if remote.is_local_source:
            resolver = RemoteResolver(GitCache(self.root_folder / ".tko" / "cache"), self.root_folder)
            remote = replace(
                remote,
                path_or_url=resolver.serialize_uri(remote),
                is_editable=resolver.is_editable_index(remote),
            )
        self.__remotes[remote.name] = remote

    def get_remote(self, name: str) -> Remote | None:
        return self.get_source(name)

    def get_source(self, name: str) -> Remote | None:
        return self.__remotes.get(name, None)

    def get_authoring_remote(self) -> Remote | None:
        return self.get_remote(self.authoring_source)

    def get_sandbox(self) -> Remote:
        remote = self.get_authoring_remote()
        if remote is None:
            raise ValueError(str(_SOURCE_NOT_FOUND).format(label=self.authoring_source))
        return remote

    def get_remotes(self) -> dict[str, Remote]:
        return self.get_sources()

    def get_sources(self) -> dict[str, Remote]:
        return dict(self.__remotes)

    def rm_remote(self, key: str) -> bool:
        return self.remove_source(key)

    def remove_source(self, label: str) -> bool:
        if label == self.authoring_source:
            raise ValueError(f"Source '{label}' is the authoring source\nSelect another authoring source before removing it")
        if label in self.__remotes:
            del self.__remotes[label]
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

    def rm_remote_legacy(self, key: str) -> bool:
        if key in self.__remotes:
            del self.__remotes[key]
            return True
        return False


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
        self.__remotes.clear()
        for label, source_data in sources_data.items():
            if not isinstance(source_data, dict):
                continue
            uri = source_data.get("uri")
            if isinstance(uri, str):
                self.set_remote(Remote.from_uri(label, uri))

    def _load_sources_list(self, sources_data: list[ConfigDict]) -> None:
        self.__remotes.clear()
        for item in sources_data:
            remote = Remote.from_dict(item)
            self.set_remote(remote)

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
        authoring_source = self._load_str(profile, "authoring_source", self.authoring_source)
        sources = self._load_dict(profile, "sources")
        if sources is not None:
            self._load_sources_map(sources)
        self.authoring_source = authoring_source
        audit_data = self._load_dict(profile, "audit")
        if audit_data is not None:
            _ = self.audit.from_dict(audit_data)

    def validate_authoring_source(self) -> None:
        if not self.authoring_source:
            raise ValueError(str(_AUTHORING_SOURCE_NOT_CONFIGURED))
        remote = self.get_remote(self.authoring_source)
        if remote is None:
            raise ValueError(str(_SOURCE_NOT_FOUND).format(label=self.authoring_source))
        resolver = RemoteResolver(GitCache(self.root_folder / ".tko" / "cache"), self.root_folder)
        if not resolver.is_local_internal(remote):
            if remote.is_git_source:
                raise ValueError(str(_SOURCE_EXTERNAL_AUTHORING).format(label=self.authoring_source))
            raise ValueError(str(_SOURCE_POINTS_OUTSIDE_WORKSPACE).format(label=self.authoring_source))
        if not resolver.is_editable_index(remote):
            raise ValueError(str(_AUTHORING_SOURCE_NOT_EDITABLE).format(label=self.authoring_source))
        activity_dir = resolver.source_activity_dir(remote)
        if activity_dir.exists() and not activity_dir.is_dir():
            raise ValueError(str(_AUTHORING_SOURCE_FOLDER_BLOCKED).format(label=self.authoring_source))

    def update_profile_from_dict(self, profile: ConfigDict) -> None:
        self._load_profile_from_dict(profile)
        self.validate_authoring_source()

    def load_from_dict(self, data: ConfigDict) -> None:
        try:
            # Load simple fields
            self.version = self._load_str(data, "version", self.version)
            profile = self._load_dict(data, "profile")
            if profile is not None:
                self._load_profile_from_dict(profile)

            preferences = self._load_dict(data, "preferences")
            if preferences is not None:
                self.lang = self._load_str(preferences, "lang", self.lang)
                self.flags = {key: value for key, value in preferences.items() if key != "lang"}
            else:
                flags = self._load_dict(data, "flags")
                if flags is not None:
                    self.flags = flags
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
                    self.__remotes.clear()
                if isinstance(sandbox_name, str):
                    self.authoring_source = sandbox_name
                if isinstance(sandbox_name, str) and isinstance(sandbox_index, str):
                    self.set_remote(Remote.from_uri(sandbox_name, sandbox_index, is_editable=True))

            audit_data = self._load_dict(data, "audit")
            if audit_data is not None:
                _ = self.audit.from_dict(audit_data)

            # Load the 'source' field with specific validation
            source_data = self._load_source_list(data, "sources")
            if source_data is not None:
                existing_authoring = self.get_remote(self.authoring_source)
                self._load_sources_list(source_data)
                if existing_authoring is not None:
                    self.set_remote(existing_authoring)
            elif "sources" in data:
                raise TypeError("The 'sources' field must be a list.")
            self.validate_authoring_source()

        except (KeyError, TypeError):
            logger.exception(str(_REPOSITORY_DATA_LOAD_ERROR))

    def to_dict(self) -> ConfigDict:
        resolver = RemoteResolver(GitCache(self.root_folder / ".tko" / "cache"), self.root_folder)
        sources: ConfigDict = {
            remote.name: {"uri": resolver.serialize_uri(remote)}
            for remote in self.__remotes.values()
        }
        profile: ConfigDict = {
            "authoring_source": self.authoring_source,
            "sources": sources,
            "audit": self.audit.to_dict(),
        }
        preferences: ConfigDict = self.flags.copy()
        preferences["lang"] = self.lang
        state: ConfigDict = {
            "expanded": list(self.expanded),
            "selected": self.selected,
            "selected_index": self.selected_index,
        }
        return {
            "version": self.version,
            "profile": profile,
            "preferences": preferences,
            "state": state,
        }
