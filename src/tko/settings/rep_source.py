from __future__ import annotations
from pathlib import Path
from typing import Any
import os
from enum import Enum

from tko.settings.git_cache import GitCache

class SourceType(Enum):
    LOCAL_FILE = "local"
    GIT_SOURCE = "git"


STUDENT_SANDBOX_NAME: str = "sandbox"

class RepSource:
    class Keys:
        NAME = "name"
        TARGET = "target"
        TYPE = "type"
        INDEX = "index"
        WRITEABLE = "writeable"
        QUESTS = "quests"
        TASKS = "tasks"
        BRANCH = "branch"


    """
    alias: str - unique identifier for the source, used to reference the source in the code and configuration
    target: str - for LOCAL_FILE, it's folder path; for GIT_CLONE, it's the git repository link
    source_type: SourceType - type of the source, either LOCAL_FILE or GIT_CLONE
    writeable: bool - indicates if the source is writeable, used to determine if the source can be modified or not
    branch: str | None - for GIT_CLONE type, it's the branch to clone or pull, default is "master"
    filters: list[str] | None - list of filters to apply when loading quests from the source, used to filter quests based on certain criteria
    """
    def __init__(self, alias: str, git_cache: GitCache | None):
        self.name: str = alias
        self.target: str = ""
        self.source_type: SourceType = SourceType.LOCAL_FILE
        self.writeable: bool = False
        self.index: str = "README.md"
        self.branch: str | None = None
        self.quests: dict[str, str] | None = None # none significa não ter filtro
        self.tasks: dict[str, str] | None = None
        self.repo_local_workspace: Path | None = None   # if read-only rep, rep folder to tasks will be, join(local_workspace, alias)
        self.repo_cache_folder: Path | None = None 
        self.git_cache = git_cache

    def set_git_cache(self, git_cache: GitCache):
        self.git_cache = git_cache
        return self

    def set_local_source(self, target: Path, writeable: bool = False):
        self.source_type = SourceType.LOCAL_FILE
        self.target = str(target)
        self.writeable = writeable
        return self
    
    def is_sandbox_source(self) -> bool:
        return self.name == STUDENT_SANDBOX_NAME
    
    def set_student_sandbox(self):
        self.name = STUDENT_SANDBOX_NAME
        self.set_local_source(target=Path(STUDENT_SANDBOX_NAME), writeable=True)
        return self
        
    def get_filters(self) -> tuple[dict[str, str] | None, dict[str, str] | None]:
        return self.quests, self.tasks

    def set_git_source(self, target: str, branch: str | None = None):
        self.source_type = SourceType.GIT_SOURCE
        self.target = target
        self.branch = branch
        return self
    
    def is_local(self) -> bool:
        return self.source_type == SourceType.LOCAL_FILE

    def set_writeable(self, writeable: bool = True):
        self.writeable = writeable
        return self

    def get_writeable(self) -> bool:
        return self.writeable
    
    def is_read_only(self) -> bool:
        if self.source_type == SourceType.LOCAL_FILE:
            return not self.writeable
        if self.source_type == SourceType.GIT_SOURCE:
            return True
        return True

    def get_url_link(self) -> str:
        if self.source_type == SourceType.GIT_SOURCE:
            return self.target
        elif self.source_type == SourceType.LOCAL_FILE:
            return self.target
        raise ValueError("Unknown source type")

    def is_git_source(self) -> bool:
        return self.source_type in [SourceType.GIT_SOURCE, "clone"] # for backward compatibility, to remove in the future

    def is_local_source(self) -> bool:
        return self.source_type == SourceType.LOCAL_FILE

    def get_source_readme(self) -> Path:
        if self.source_type == SourceType.LOCAL_FILE:
            file: str = os.path.join(self.target, self.index)
            if os.path.isabs(file):
                return Path(file)
            else:
                return self.get_workspace() / file
        if self.source_type == SourceType.GIT_SOURCE:
            return self.get_source_folder() / self.index
        raise ValueError("Unknown source type")
    
    def get_source_folder(self) -> Path:
        if self.source_type == SourceType.LOCAL_FILE:
            return Path(self.target)
        if self.source_type == SourceType.GIT_SOURCE:
            if self.git_cache is None:
                raise ValueError("Git cache is not set for git source")
            return self.git_cache.get(self.get_url_link())# absolute path to cached repo
        raise ValueError("Unknown source type")

    
    def set_filters(self, quests: dict[str, str] | None, tasks: dict[str, str] | None = None):
        self.quests = quests
        self.tasks = tasks
        return self
    
    def set_source_globals(self, root_workspace: Path, cache_folder: Path):
        self.repo_local_workspace = root_workspace / self.name
        self.repo_cache_folder = cache_folder

    def get_cache_folder(self) -> Path:
        if self.repo_cache_folder is None:
            raise ValueError("Local cache folder is not set")
        return self.repo_cache_folder

    def get_workspace(self) -> Path:
        if self.repo_local_workspace is None:
            raise ValueError("Local workspace is not set")
        return self.repo_local_workspace
    
    def get_task_workspace(self, task_key: str) -> Path:
        if not self.is_read_only():
            raise ValueError("Source is not read-only, task workspace is the same as source workspace")
        return self.get_workspace() / task_key

    def load_from_dict(self, data: dict[str, Any]):
        Keys = RepSource.Keys
        if Keys.NAME in data and isinstance(data[Keys.NAME], str):
            self.name = data[Keys.NAME]
        if "alias" in data and isinstance(data["alias"], str): # for backward compatibility
            self.name = data["alias"]
        if "database" in data and isinstance(data["database"], str): # for backward compatibility
            self.name = data["database"]
        if Keys.TARGET in data and isinstance(data[Keys.TARGET], str):
            self.target = data[Keys.TARGET]
        if "link" in data and isinstance(data["link"], str): # for backward compatibility
            self.target = data["link"]
            if self.target.endswith("README.md"):
                self.target = os.path.dirname(self.target)
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
        if Keys.QUESTS in data and isinstance(data[Keys.QUESTS], list):
            self.quests = {q:"" for q in data[Keys.QUESTS]}
        if Keys.QUESTS in data and isinstance(data[Keys.QUESTS], dict):
            self.quests = {q: v for q, v in data[Keys.QUESTS].items()}

        if "filters" in data and isinstance(data["filters"], list): # for backward compatibility
            self.quests = {q: "" for q in data["filters"]} # type: ignore
        if "filters" in data and isinstance(data["filters"], dict): # for backward compatibility
            self.quests = {q: v for q, v in data["filters"].items()} # type: ignore
        
        if Keys.TASKS in data and isinstance(data[Keys.TASKS], list):
            self.tasks = {t: "" for t in data[Keys.TASKS]}
        if Keys.TASKS in data and isinstance(data[Keys.TASKS], dict):
            self.tasks = {t: v for t, v in data[Keys.TASKS].items()}
            
        if Keys.WRITEABLE in data and isinstance(data[Keys.WRITEABLE], bool):
            self.writeable = data[Keys.WRITEABLE]
        if self.name == STUDENT_SANDBOX_NAME: # for backward compatibility, to remove in the future
            self.writeable = True
        if Keys.INDEX in data and isinstance(data[Keys.INDEX], str):
            self.index = data[Keys.INDEX]
        else:
            self.index = "README.md"
        return self

    def save_to_dict(self) -> dict[str, Any]:
        Keys = RepSource.Keys
        output: dict[str, Any] = {
            Keys.NAME: self.name,
            Keys.TARGET: self.target,
            Keys.INDEX: self.index,
            Keys.TYPE: self.source_type.value,
            Keys.WRITEABLE: self.writeable,
        }
        if self.branch is not None and self.branch != "master":
            output[Keys.BRANCH] = self.branch
        output[Keys.QUESTS] = None if self.quests is None else { k: v for k, v in self.quests.items() }
        output[Keys.TASKS] = None if self.tasks is None else { k: v for k, v in self.tasks.items() }
        return output
