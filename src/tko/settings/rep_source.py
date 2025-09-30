from typing import Any
import os

class RepSource:
    class Keys:
        DATABASE = "database"
        LINK = "link"
        CACHE_PATH = "cache_path"
        CACHE_TIMESTAMP = "cache_timestamp"
        FILTERS = "filters"

    def __init__(self, database: str, link: str, filters: list[str] | None):
        self.database = database
        self.link = link
        self.cache_path: str = ""
        self.cache_timestamp: str = ""
        self.filters: list[str] | None = filters
        self.local_rep_folder: str | None = None
        self.local_cache_folder: str | None = None

    def set_database(self, database: str):
        self.database = database
        return self

    def set_link(self, link: str):
        self.link = link
        return self

    def set_cache_path(self, cache_path: str):
        self.cache_path = cache_path
        return self

    def set_cache_timestamp(self, cache_timestamp: str):
        self.cache_timestamp = cache_timestamp
        return self
    
    def set_filters(self, filters: list[str] | None):
        self.filters = filters
        return self
    
    def set_local_info(self, rep_folder: str, cache_folder: str):
        self.local_rep_folder = rep_folder
        self.local_cache_folder = cache_folder

    def get_local_cache_path(self) -> str:
        if self.local_cache_folder is None:
            raise ValueError("Local cache folder is not set")
        return os.path.abspath(os.path.join(self.local_cache_folder, self.database + ".md"))

    def get_rep_folder(self) -> str:
        if self.local_rep_folder is None:
            raise ValueError("Local rep folder is not set")
        return self.local_rep_folder
    
    def get_local_database_path(self) -> str:
        return os.path.abspath(os.path.join(self.get_rep_folder(), self.database))

    def load_from_dict(self, data: dict[str, Any]):
        Keys = RepSource.Keys
        if Keys.DATABASE in data and isinstance(data[Keys.DATABASE], str):
            self.database = data[Keys.DATABASE]

        if Keys.LINK in data and isinstance(data[Keys.LINK], str):
            self.link = data[Keys.LINK]
        if Keys.CACHE_PATH in data and isinstance(data[Keys.CACHE_PATH], str):
            self.cache_path = data[Keys.CACHE_PATH]
        if Keys.CACHE_TIMESTAMP in data and isinstance(data[Keys.CACHE_TIMESTAMP], str):
            self.cache_timestamp = data[Keys.CACHE_TIMESTAMP]
        if Keys.FILTERS in data and isinstance(data[Keys.FILTERS], list):
            self.filters = data[Keys.FILTERS]
        return self

    def save_to_dict(self) -> dict[str, Any]:
        Keys = RepSource.Keys
        return {
            Keys.DATABASE: self.database,
            Keys.LINK: self.link,
            Keys.CACHE_PATH: self.cache_path,
            Keys.CACHE_TIMESTAMP: self.cache_timestamp,
            Keys.FILTERS: self.filters
        }
