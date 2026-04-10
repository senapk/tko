from tko.settings.git_cache import GitCache
from tko.settings.rep_source import STUDENT_SANDBOX_NAME, RepSource

from typing import Any

class RepData:
    def __init__(self, git_cache: GitCache):
        self.version: str = ""
        self.__sources: list[RepSource] = []
        self.expanded: list[str] = []
        self.flags: dict[str, Any] = {}
        self.lang: str = ""
        self.selected: str = ""
        self.git_cache = git_cache

    def set_source(self, source: RepSource):
        for i, s in enumerate(self.__sources):
            if s.name == source.name:
                self.__sources[i] = source
                return self
        self.__sources.append(source)

    def del_source(self, alias: str):
        self.__sources = [s for s in self.__sources if s.name != alias]
        return self

    def get_source(self, alias: str) -> RepSource | None:
        for s in self.__sources:
            if s.name == alias:
                return s
        return None

    def __ensure_sandbox_source(self) -> None:
        sandbox_source = self.get_source(STUDENT_SANDBOX_NAME)
        if sandbox_source is None:
            sandbox_source = RepSource(STUDENT_SANDBOX_NAME, git_cache=None).set_default_student_sandbox()
            self.set_source(sandbox_source)
            # readme = sandbox_source.get_source_readme()
            # if not readme.exists():
            #     readme.parent.mkdir(parents=True, exist_ok=True)
            #     readme.touch()

    # fonte local é retornada primeiro para garantir que ela seja priorizada em relação a fontes externas
    # sandbox é sempre a primeira fonte local, para garantir que ela seja priorizada em relação a outras fontes locais
    def get_sources(self) -> list[RepSource]:
        self.__ensure_sandbox_source()
        external_sources: list[RepSource] = []
        sandbox_source: list[RepSource] = []
        for s in self.__sources:
            if s.is_sandbox_source():
                sandbox_source.append(s)
            else:
                external_sources.append(s)
        return sandbox_source + external_sources

    def get_expanded(self) -> list[str]:
        return self.expanded

    # def get_tasks(self) -> dict[str, Any]:
    #     return self.tasks

    def get_flags(self) -> dict[str, Any]:
        return self.flags

    def get_lang(self) -> str:
        return self.lang

    def get_selected(self) -> str:
        return self.selected

    def set_lang(self, lang: str):
        self.lang = lang
        return self

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
            # Load the 'source' field with specific validation
            if "sources" in data:
                source_data: list[dict[str, Any]] = data["sources"]
                if isinstance(source_data, list): # type: ignore
                    self.__sources = [RepSource("", git_cache=self.git_cache).load_from_dict(x) for x in source_data]
                else:
                    raise TypeError("The 'sources' field must be a list.")

        except (KeyError, TypeError) as e:
            print(f"Error loading data from dictionary: {e}")

    def save_to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "sources": [x.save_to_dict() for x in self.__sources],
            "expanded": self.expanded,
            "flags": self.flags,
            "lang": self.lang,
            "selected": self.selected,
        }