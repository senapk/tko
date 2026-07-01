from __future__ import annotations
from dataclasses import dataclass
from loguru import logger
from tko.i18n import Msg
from tko.repository.remote import Remote

from typing import Any



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
    def __init__(self):
        self.version: str = ""
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

    def set_remote(self, source: Remote) -> None:
        self.__remotes[source.data.name] = source

    def del_remote(self, alias: str) -> bool:
        if alias in self.__remotes:
            del self.__remotes[alias]
            return True
        return False

    def get_remote(self, alias: str) -> Remote | None:
        return self.__remotes.get(alias)

    def get_sandbox(self) -> Remote | None:
        for s in self.__remotes.values():
            if s.is_sandbox():
                return s
        return None

    def __ensure_sandbox_source(self) -> None:
        sandbox_source = self.get_sandbox()
        if sandbox_source is None:
            sandbox_source = Remote("")
            sandbox_source.set_sandbox()
            self.set_remote(sandbox_source)

    # fonte local é retornada primeiro para garantir que ela seja priorizada em relação a fontes externas
    # sandbox é sempre a primeira fonte local, para garantir que ela seja priorizada em relação a outras fontes locais
    @property
    def remotes_raw_list(self) -> list[Remote]:
        self.__ensure_sandbox_source()
        external_sources: list[Remote] = []
        sandbox_source: list[Remote] = []
        for s in self.__remotes.values():
            if s.is_sandbox():
                sandbox_source.append(s)
            else:
                external_sources.append(s)
        return sandbox_source + external_sources

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
                    remotes = [Remote("").load_from_dict(x) for x in source_data]
                    self.__remotes = {remote.data.name: remote for remote in remotes}
                else:
                    raise TypeError("The 'sources' field must be a list.")

        except (KeyError, TypeError):
            logger.exception(str(_REPOSITORY_DATA_LOAD_ERROR))

    def save_to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "sources": [x.save_to_dict() for x in self.remotes_raw_list],
            "expanded": self.expanded,
            "flags": self.flags,
            "audit": self.audit.to_dict(),
            "lang": self.lang,
            "selected": self.selected,
            "selected_index": self.selected_index,
        }