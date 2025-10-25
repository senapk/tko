from tko.settings.rep_source import RepSource


from typing import Any


class RepData:
    def __init__(self):
        self.version: str = ""
        self.__sources: list[RepSource] = []
        self.expanded: list[str] = []
        self.tasks: dict[str, Any] = {}
        self.flags: dict[str, Any] = {}
        self.lang: str = ""
        self.selected: str = ""

    def set_source(self, source: RepSource):
        for i, s in enumerate(self.__sources):
            if s.database == source.database:
                self.__sources[i] = source
                return self
        self.__sources.append(source)

    def get_source(self, database: str) -> RepSource | None:
        for s in self.__sources:
            if s.database == database:
                return s
        return None

    def get_sources(self) -> list[RepSource]:
        return self.__sources

    def get_expanded(self) -> list[str]:
        return self.expanded

    def get_tasks(self) -> dict[str, Any]:
        return self.tasks

    def get_flags(self) -> dict[str, Any]:
        return self.flags

    def get_lang(self) -> str:
        return self.lang

    def get_selected(self) -> str:
        return self.selected

    def get_database(self) -> str:
        return self.database

    def set_lang(self, lang: str):
        self.lang = lang
        return self

    def set_database(self, database: str):
        self.database = database
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
            self.tasks = self._safe_load(data, "tasks", dict, self.tasks)
            self.flags = self._safe_load(data, "flags", dict, self.flags)
            self.lang = self._safe_load(data, "lang", str, self.lang)
            self.selected = self._safe_load(data, "selected", str, self.selected)

            # Load the 'source' field with specific validation
            if "sources" in data:
                source_data: list[dict[str, Any]] = data["sources"]
                if isinstance(source_data, list): # type: ignore
                    self.__sources = [RepSource("", "", RepSource.Type.LINK, None).load_from_dict(x) for x in source_data]
                else:
                    raise TypeError("The 'sources' field must be a list.")

        except (KeyError, TypeError) as e:
            print(f"Error loading data from dictionary: {e}")
            # Optionally, you can re-raise the exception or handle it differently
            # raise ValueError("Malformed data for RepData") from e

    def save_to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "sources": [x.save_to_dict() for x in self.__sources],
            "expanded": self.expanded,
            "tasks": self.tasks,
            "flags": self.flags,
            "lang": self.lang,
            "selected": self.selected,
        }