from __future__ import annotations
from typing import Any
import os
from enum import Enum

class SourceType(Enum):
    LOCAL_FILE = "local"
    GIT_SOURCE = "git"

class RepSource:
    STUDENT_SANDBOX_ALIAS = "sandbox"

    default_draft_folder = "00_rascunhos"

    sandbox_readme_content = (
        "#Sandbox\n"
        "## Sandbox\n"
        "<!--autoload_cluster=.-->\n"
    )

    class Keys:
        ALIAS = "alias"
        TARGET = "target"
        TYPE = "type"
        WRITEABLE = "writeable"
        GIT_CACHE_TIMESTAMP = "cache_timestamp"
        GIT_CACHE_PATH = "cache_path"
        FILTERS = "filters"
        BRANCH = "branch"

    """
    alias: str - unique identifier for the source, used to reference the source in the code and configuration
    target: str - for LOCAL_FILE, it's folder path; for GIT_CLONE, it's the git repository link
    source_type: SourceType - type of the source, either LOCAL_FILE or GIT_CLONE
    cache_timestamp: str - timestamp of the last update of the source, used for caching purposes
    writeable: bool - indicates if the source is writeable, used to determine if the source can be modified or not
    branch: str | None - for GIT_CLONE type, it's the branch to clone or pull, default is "master"
    filters: list[str] | None - list of filters to apply when loading quests from the source, used to filter quests based on certain criteria
    """
    def __init__(self, alias: str):
        self.alias = alias
        self.__target = ""
        self.source_type: SourceType = SourceType.LOCAL_FILE
        self.cache_timestamp: str = ""
        self.__writeable: bool = False
        self.branch: str | None = None
        self.filters: list[str] | None = None
        self.rep_local_workspace: str | None = None   # if read-only rep, rep folder to tasks will be, join(local_workspace, alias)
        self.rep_cache_folder: str | None = None  # if git clone rep, cache folder to git clone will be, join(git_cache_folder, alias)

    def set_local_source(self, target: str, writeable: bool = False):
        self.source_type = SourceType.LOCAL_FILE
        self.__target = target
        self.__writeable = writeable
        return self
    
    def is_sandbox_source(self) -> bool:
        return self.alias == RepSource.STUDENT_SANDBOX_ALIAS # for backward compatibility, to remove in the future
    
    def set_student_sandbox(self):
        self.alias = RepSource.STUDENT_SANDBOX_ALIAS
        self.set_local_source(target=RepSource.STUDENT_SANDBOX_ALIAS, writeable=True)
        return self
    
    def get_default_sandbox_draft_folder(self) -> str:
        return self.default_draft_folder
    
    def ensure_sandbox_source(self, local_workspace: str):
        # create folder sandbox inside rep_workspace if not exists
        sandbox_path = os.path.join(local_workspace, RepSource.STUDENT_SANDBOX_ALIAS)
        if not os.path.exists(sandbox_path):
            os.makedirs(sandbox_path)
        readme_file = os.path.join(sandbox_path, "Readme.md")
        if not os.path.exists(readme_file):
            with open(readme_file, "w") as f:
                f.write(self.sandbox_readme_content)
        return self
    
    def get_filters(self) -> list[str] | None:
        return self.filters

    def set_git_source(self, target: str, branch: str | None = None):
        self.source_type = SourceType.GIT_SOURCE
        self.__target = target
        self.branch = branch
        return self
    
    def is_local(self) -> bool:
        return self.source_type == SourceType.LOCAL_FILE

    def set_writeable(self, writeable: bool = True):
        self.__writeable = writeable
        return self

    def get_writeable(self) -> bool:
        return self.__writeable
    
    def is_read_only(self) -> bool:
        if self.source_type == SourceType.LOCAL_FILE:
            return not self.__writeable
        if self.source_type == SourceType.GIT_SOURCE:
            return True
        return True

    def get_url_link(self) -> str:
        if self.source_type == SourceType.GIT_SOURCE:
            return self.__target
        raise ValueError("Unknown source type")

    def is_git_source(self) -> bool:
        return self.source_type in [SourceType.GIT_SOURCE, "clone"] # for backward compatibility, to remove in the future

    def is_local_source(self) -> bool:
        return self.source_type == SourceType.LOCAL_FILE

    def get_source_readme(self) -> str:
        if self.source_type == SourceType.LOCAL_FILE:
            return os.path.join(self.__target, "Readme.md")
        if self.source_type == SourceType.GIT_SOURCE:
            return os.path.join(self.get_source_cache_folder(),"Readme.md")
        raise ValueError("Unknown source type")
    
    def get_source_folder(self) -> str:
        if self.source_type == SourceType.LOCAL_FILE:
            return self.__target
        if self.source_type == SourceType.GIT_SOURCE:
            return self.get_source_cache_folder()
        raise ValueError("Unknown source type")

    def set_cache_timestamp(self, cache_timestamp: str):
        self.cache_timestamp = cache_timestamp
        return self
    
    def set_filters(self, filters: list[str] | None):
        self.filters = filters
        return self
    
    def set_rep_globals(self, local_workspace: str, cache_folder: str):
        self.rep_local_workspace = local_workspace
        self.rep_cache_folder = cache_folder

    def get_source_cache_folder(self) -> str:
        if self.rep_cache_folder is None:
            raise ValueError("Local rep folder is not set")
        return os.path.join(self.rep_cache_folder, self.alias)

    def get_rep_cache_folder(self) -> str:
        if self.rep_cache_folder is None:
            raise ValueError("Local cache folder is not set")
        return self.rep_cache_folder

    def get_rep_workspace(self) -> str:
        if self.rep_local_workspace is None:
            raise ValueError("Local workspace is not set")
        return self.rep_local_workspace
    
    def get_source_workspace(self) -> str:
        return os.path.abspath(os.path.join(self.get_rep_workspace(), self.alias))
    
    def get_task_workspace(self, task_key: str) -> str:
        if not self.is_read_only():
            raise ValueError("Source is not read-only, task workspace is the same as source workspace")
        return os.path.join(self.get_source_workspace(), task_key)

    def load_from_dict(self, data: dict[str, Any]):
        Keys = RepSource.Keys
        if Keys.ALIAS in data and isinstance(data[Keys.ALIAS], str):
            self.alias = data[Keys.ALIAS]
        if "database" in data and isinstance(data["database"], str): # for backward compatibility
            self.alias = data["database"]
        if Keys.TARGET in data and isinstance(data[Keys.TARGET], str):
            self.__target = data[Keys.TARGET]
        if "link" in data and isinstance(data["link"], str): # for backward compatibility
            self.__target = data["link"]
            if self.__target.endswith("Readme.md"):
                self.__target = os.path.dirname(self.__target)
        if Keys.BRANCH in data and isinstance(data[Keys.BRANCH], str):
            self.branch = data[Keys.BRANCH]
        else:
            self.branch = "master"
        if Keys.TYPE in data and isinstance(data[Keys.TYPE], str):
            type_str = data[Keys.TYPE]
            if type_str == SourceType.LOCAL_FILE.value:
                self.source_type = SourceType.LOCAL_FILE
            else:
                self.source_type = SourceType.GIT_SOURCE
        else:
            self.source_type = SourceType.LOCAL_FILE
        if Keys.GIT_CACHE_TIMESTAMP in data and isinstance(data[Keys.GIT_CACHE_TIMESTAMP], str):
            self.cache_timestamp = data[Keys.GIT_CACHE_TIMESTAMP]
        if Keys.FILTERS in data and isinstance(data[Keys.FILTERS], list):
            self.filters = data[Keys.FILTERS]
        if Keys.WRITEABLE in data and isinstance(data[Keys.WRITEABLE], bool):
            self.__writeable = data[Keys.WRITEABLE]
        if self.alias == RepSource.STUDENT_SANDBOX_ALIAS or self.alias == "local": # for backward compatibility, to remove in the future
            self.__writeable = True
        return self

    def save_to_dict(self) -> dict[str, Any]:
        Keys = RepSource.Keys
        output: dict[str, Any] = {
            Keys.ALIAS: self.alias,
            Keys.TARGET: self.__target,
            Keys.TYPE: self.source_type.value,
            Keys.WRITEABLE: self.__writeable,
        }
        if self.branch is not None and self.branch != "master":
            output[Keys.BRANCH] = self.branch
        if self.cache_timestamp:
            output[Keys.GIT_CACHE_TIMESTAMP] = self.cache_timestamp
        if self.filters is not None:
            output[Keys.FILTERS] = self.filters
        return output
