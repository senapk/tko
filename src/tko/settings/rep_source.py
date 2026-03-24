from __future__ import annotations
from pathlib import Path
from typing import Any
import os
from enum import Enum

from tko.settings.git_cache import GitCache

class SourceType(Enum):
    LOCAL_FILE = "local"
    GIT_SOURCE = "git"

class RepSource:
    STUDENT_SANDBOX_NAME = "sandbox"

    DEFAULT_DRAFT_FOLDER = "00_rascunhos"

    AUTOLOAD_CLUSTER_COMMAND = "autoload_cluster"
    AUTOLOAD_QUEST_COMMAND = "autoload_quest"

    sandbox_readme_content = f"""
# Sandbox

Cada vez que criar um rascunho, ele será salvo na pasta `{DEFAULT_DRAFT_FOLDER}` dentro do sandbox.

Você pode criar quantos rascunhos quiser. Eles serão rastreados pela chave key no preâmbulo do rascunho.

Renomeie o nome da pasta para renomear o rascunho. Exclua a pasta para excluir o rascunho.

Sinta-se à vontade para organizar seus rascunhos em subpastas dentro do sandbox, se desejar.

## {STUDENT_SANDBOX_NAME}
<!--{AUTOLOAD_CLUSTER_COMMAND}=.-->
"""[1:]
    

    class Keys:
        NAME = "name"
        TARGET = "target"
        TYPE = "type"
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
    def __init__(self, alias: str):
        self.name = alias
        self.__target = ""
        self.source_type: SourceType = SourceType.LOCAL_FILE
        self.__writeable: bool = False
        self.branch: str | None = None
        self.quests: list[str] | None = None
        self.tasks: list[str] | None = None
        self.rep_local_workspace: Path | None = None   # if read-only rep, rep folder to tasks will be, join(local_workspace, alias)
        self.rep_cache_folder: Path | None = None 

    def set_local_source(self, target: Path, writeable: bool = False):
        self.source_type = SourceType.LOCAL_FILE
        self.__target = str(target)
        self.__writeable = writeable
        return self
    
    def is_sandbox_source(self) -> bool:
        return self.name == RepSource.STUDENT_SANDBOX_NAME # for backward compatibility, to remove in the future
    
    def set_student_sandbox(self):
        self.name = RepSource.STUDENT_SANDBOX_NAME
        self.set_local_source(target=Path(RepSource.STUDENT_SANDBOX_NAME), writeable=True)
        return self
    
    def get_default_sandbox_draft_folder(self) -> str:
        return self.DEFAULT_DRAFT_FOLDER
    
    def ensure_sandbox_source(self, local_workspace: Path):
        # create folder sandbox inside rep_workspace if not exists
        sandbox_path = local_workspace / RepSource.STUDENT_SANDBOX_NAME
        sandbox_path.mkdir(parents=True, exist_ok=True)
        readme_file = sandbox_path / "README.md"
        if not os.path.exists(readme_file):
            with open(readme_file, "w") as f:
                f.write(self.sandbox_readme_content)
        return self
    
    # return quests and tasks filters
    def get_filters(self) -> tuple[list[str] | None, list[str] | None]:
        return self.quests, self.tasks

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
        elif self.source_type == SourceType.LOCAL_FILE:
            return self.__target
        raise ValueError("Unknown source type")

    def is_git_source(self) -> bool:
        return self.source_type in [SourceType.GIT_SOURCE, "clone"] # for backward compatibility, to remove in the future

    def is_local_source(self) -> bool:
        return self.source_type == SourceType.LOCAL_FILE

    def get_source_readme(self) -> Path:
        if self.source_type == SourceType.LOCAL_FILE:
            
            file: str = os.path.join(self.__target, "README.md")
            if os.path.isabs(file):
                return Path(file)
            else:
                return self.get_rep_workspace() / file
        if self.source_type == SourceType.GIT_SOURCE:
            return self.get_source_folder() / "README.md"
        raise ValueError("Unknown source type")
    
    def get_source_folder(self) -> Path:
        if self.source_type == SourceType.LOCAL_FILE:
            return Path(self.__target)
        if self.source_type == SourceType.GIT_SOURCE:
            git_cache = GitCache(self.get_rep_cache_folder())
            return git_cache.get(self.get_url_link(), force_update=False)# absolute path to cached repo
        raise ValueError("Unknown source type")

    
    def set_filters(self, quests: list[str] | None, tasks: list[str] | None = None):
        self.quests = quests
        self.tasks = tasks
        return self
    
    def set_rep_globals(self, local_workspace: Path, cache_folder: Path):
        self.rep_local_workspace = local_workspace
        self.rep_cache_folder = cache_folder

    def get_rep_cache_folder(self) -> Path:
        if self.rep_cache_folder is None:
            raise ValueError("Local cache folder is not set")
        return self.rep_cache_folder

    def get_rep_workspace(self) -> Path:
        if self.rep_local_workspace is None:
            raise ValueError("Local workspace is not set")
        return self.rep_local_workspace
    
    def get_source_workspace(self) -> Path:
        return self.get_rep_workspace() / self.name
    
    def get_task_workspace(self, task_key: str) -> Path:
        if not self.is_read_only():
            raise ValueError("Source is not read-only, task workspace is the same as source workspace")
        return self.get_source_workspace() / task_key

    def load_from_dict(self, data: dict[str, Any]):
        Keys = RepSource.Keys
        if Keys.NAME in data and isinstance(data[Keys.NAME], str):
            self.name = data[Keys.NAME]
        if "alias" in data and isinstance(data["alias"], str): # for backward compatibility
            self.name = data["alias"]
        if "database" in data and isinstance(data["database"], str): # for backward compatibility
            self.name = data["database"]
        if Keys.TARGET in data and isinstance(data[Keys.TARGET], str):
            self.__target = data[Keys.TARGET]
        if "link" in data and isinstance(data["link"], str): # for backward compatibility
            self.__target = data["link"]
            if self.__target.endswith("README.md"):
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
        if Keys.QUESTS in data and isinstance(data[Keys.QUESTS], list):
            self.quests = data[Keys.QUESTS]
        if "filters" in data and isinstance(data["filters"], list): # for backward compatibility
            self.quests = data["filters"]
        if Keys.TASKS in data and isinstance(data[Keys.TASKS], list):
            self.tasks = data[Keys.TASKS]
        if Keys.WRITEABLE in data and isinstance(data[Keys.WRITEABLE], bool):
            self.__writeable = data[Keys.WRITEABLE]
        if self.name == RepSource.STUDENT_SANDBOX_NAME or self.name == "local": # for backward compatibility, to remove in the future
            self.__writeable = True
        return self

    def save_to_dict(self) -> dict[str, Any]:
        Keys = RepSource.Keys
        output: dict[str, Any] = {
            Keys.NAME: self.name,
            Keys.TARGET: self.__target,
            Keys.TYPE: self.source_type.value,
            Keys.WRITEABLE: self.__writeable,
        }
        if self.branch is not None and self.branch != "master":
            output[Keys.BRANCH] = self.branch
        output[Keys.QUESTS] = self.quests
        output[Keys.TASKS] = self.tasks
        return output
