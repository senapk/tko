from __future__ import annotations
from dataclasses import dataclass, replace
from loguru import logger
from tko.i18n import Msg
from tko.repository.remote import Remote
from tko.repository.sandbox import Sandbox
from typing import Any
from pathlib import Path


_REPOSITORY_DATA_LOAD_ERROR = Msg.text(
    pt="Erro ao carregar dados do dicionário",
    en="Error loading data from dictionary",
)


@dataclass
class AuditConfig:
    enabled: bool = False
    interval_seconds: int | None = None

    def from_dict(self, data: dict[str, Any]) -> AuditConfig:
        enabled = data.get("enabled")
        if isinstance(enabled, bool):
            self.enabled = enabled

        interval_seconds = data.get("interval_seconds")
        if isinstance(interval_seconds, int):
            self.interval_seconds = interval_seconds
        elif interval_seconds is None:
            self.interval_seconds = None

        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "interval_seconds": self.interval_seconds,
        }

class RepositoryData:
    def __init__(self, root_folder: Path):
        self.root_folder: Path = root_folder
        self.version: str = ""
        self.sandbox_dir: str = ""
        self.__remotes: dict[str, Remote] = {}
        self.expanded: list[str] = []
        self.flags: dict[str, Any] = {}
        self.audit: AuditConfig = AuditConfig()
        self.lang: str = ""
        self.selected: str = ""
        self.selected_index: int = 0

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
        if remote.is_local_source:
            if not Path(remote.path_or_url).is_absolute():
                remote = replace(remote, path_or_url=Path(self.root_folder, remote.path_or_url).resolve().as_posix())
            elif  Path(remote.path_or_url).resolve().is_relative_to(self.root_folder.resolve()):
                remote = replace(remote, path_or_url=Path(remote.path_or_url).resolve().relative_to(self.root_folder.resolve()).as_posix())
        self.__remotes[remote.name] = remote

    def get_remote(self, name: str) -> Remote | None:
        return self.__remotes.get(name, None)

    def get_sandbox(self) -> Remote:
        remote = self.__remotes.get(Sandbox.get_sandbox_name(), None)
        if remote is not None:
            return remote
        return self.__ensure_sandbox_source()

    def __ensure_sandbox_source(self) -> Remote:
        if Sandbox.get_sandbox_name() in self.__remotes:
            return self.__remotes[Sandbox.get_sandbox_name()]
        sandbox_remote = Sandbox.create_default_sandbox_remote()
        self.__remotes[sandbox_remote.name] = sandbox_remote
        return sandbox_remote

    # fonte local é retornada primeiro para garantir que ela seja priorizada em relação a fontes externas
    # sandbox é sempre a primeira fonte local, para garantir que ela seja priorizada em relação a outras fontes locais
    @property
    def get_remotes(self) -> dict[str, Remote]:
        self.__ensure_sandbox_source()
        external_sources: dict[str, Remote] = {}
        sandbox_source: dict[str, Remote] = {}
        for s in self.__remotes.values():
            if Sandbox.is_sandbox(s):
                sandbox_source[s.name] = s
            else:
                external_sources[s.name] = s
        return {**sandbox_source, **external_sources}

    def _safe_load(self, data: dict[str, Any], key: str, target_type: type, default_value: Any = None):
        """Helper method to safely load a value from a dictionary."""
        if key in data and isinstance(data[key], target_type):
            return data[key]
        return default_value

    def load_from_dict(self, data: dict[str, Any]):
        try:
            # Load simple fields
            self.version = self._safe_load(data, "version", str, self.version)
            self.expanded = self._safe_load(data, "expanded", list, self.expanded)
            # self.tasks = self._safe_load(data, "tasks", dict, self.tasks)
            self.flags = self._safe_load(data, "flags", dict, self.flags)
            audit_data = self._safe_load(data, "audit", dict, None)
            if isinstance(audit_data, dict):
                self.audit.from_dict(audit_data) # type: ignore
            self.lang = self._safe_load(data, "lang", str, self.lang)
            self.selected = self._safe_load(data, "selected", str, self.selected)
            self.selected_index = self._safe_load(data, "selected_index", int, self.selected_index)

            # Load the 'source' field with specific validation
            if "sources" in data:
                source_data: list[dict[str, Any]] = data["sources"]
                if isinstance(source_data, list): # type: ignore
                    remotes = [Remote.from_dict(x) for x in source_data]
                    self.__remotes.clear()
                    for r in remotes:
                        self.set_remote(r)
                else:
                    raise TypeError("The 'sources' field must be a list.")

        except (KeyError, TypeError):
            logger.exception(str(_REPOSITORY_DATA_LOAD_ERROR))

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "sources": [x.to_dict() for x in self.get_remotes.values()],
            "expanded": self.expanded,
            "flags": self.flags,
            "audit": self.audit.to_dict(),
            "lang": self.lang,
            "selected": self.selected,
            "selected_index": self.selected_index,
        }