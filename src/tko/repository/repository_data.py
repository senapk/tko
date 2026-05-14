from tko.repository.remote import Remote

from typing import Any

class RepositoryData:
    def __init__(self):
        self.version: str = ""
        self.__remotes: list[Remote] = []
        self.expanded: list[str] = []
        self.flags: dict[str, Any] = {}
        self.lang: str = ""
        self.selected: str = ""
        self.selected_index: int = 0

    def set_remote(self, source: Remote):
        for i, s in enumerate(self.__remotes):
            if s.data.name == source.data.name:
                self.__remotes[i] = source
                return self
        self.__remotes.append(source)

    def del_remote(self, alias: str):
        self.__remotes = [s for s in self.__remotes if s.data.name != alias]
        return self

    def get_remote(self, alias: str) -> Remote | None:
        for s in self.__remotes:
            if s.data.name == alias:
                return s
        return None

    def get_sandbox(self) -> Remote | None:
        for s in self.__remotes:
            if s.is_sandbox:
                return s
        return None

    def __ensure_sandbox_source(self) -> None:
        sandbox_source = self.get_sandbox()
        if sandbox_source is None:
            sandbox_source = Remote("")
            sandbox_source.is_sandbox = True
            self.set_remote(sandbox_source)

    # fonte local é retornada primeiro para garantir que ela seja priorizada em relação a fontes externas
    # sandbox é sempre a primeira fonte local, para garantir que ela seja priorizada em relação a outras fontes locais
    @property
    def remotes_raw_list(self) -> list[Remote]:
        self.__ensure_sandbox_source()
        external_sources: list[Remote] = []
        sandbox_source: list[Remote] = []
        for s in self.__remotes:
            if s.is_sandbox:
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
            self.lang = self._safe_load(data, "lang", str, self.lang)
            self.selected = self._safe_load(data, "selected", str, self.selected)
            self.selected_index = self._safe_load(data, "selected_index", int, self.selected_index)

            # Load the 'source' field with specific validation
            if "sources" in data:
                source_data: list[dict[str, Any]] = data["sources"]
                if isinstance(source_data, list): # type: ignore
                    self.__remotes = [Remote("").load_from_dict(x) for x in source_data]
                else:
                    raise TypeError("The 'sources' field must be a list.")

        except (KeyError, TypeError) as e:
            print(f"Error loading data from dictionary: {e}")

    def save_to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "sources": [x.save_to_dict() for x in self.__remotes],
            "expanded": self.expanded,
            "flags": self.flags,
            "lang": self.lang,
            "selected": self.selected,
            "selected_index": self.selected_index,
        }