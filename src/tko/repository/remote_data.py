
from enum import Enum
from pathlib import Path

class SourceType(Enum):
    LOCAL_FILE = "local"
    GIT_SOURCE = "git"

"""
alias: str - unique identifier for the source, used to reference the source in the code and configuration
target: str - for LOCAL_FILE, it's folder path; for GIT_CLONE, it's the git repository link
source_type: SourceType - type of the source, either LOCAL_FILE or GIT_CLONE
writeable: bool - indicates if the source is writeable, used to determine if the source can be modified or not
branch: str | None - for GIT_CLONE type, it's the branch to clone or pull, default is "master"
filters: list[str] | None - list of filters to apply when loading quests from the source, used to filter quests based on certain criteria
"""

class RemoteData:
    def __init__(self, name: str = ""):
        self.name: str = name
        self.target: str = ""
        self.source_type: SourceType = SourceType.LOCAL_FILE
        self.is_editable: bool = False
        self.index: str = "README.md"
        self.branch: str | None = None
        self.quest_filters: dict[str, str] | None = None # none significa não ter filtro

    def set_local_source(self, target: Path, is_editable: bool = False, index: str | None = None):
        self.source_type = SourceType.LOCAL_FILE
        self.target = str(target)
        self.is_editable = is_editable
        if index is not None:
            self.index = index
        return self
        
    def set_git_source(self, target: str, branch: str | None = None, index: str | None = None):
        self.source_type = SourceType.GIT_SOURCE
        self.target = target
        self.branch = branch
        self.is_editable = False
        if index is not None:
            self.index = index
        return self
        
    @property
    def git_url(self) -> str | None:
        if self.is_git_source:
            return self.target
        return None


    @property
    def is_git_source(self) -> bool:
        return self.source_type in [SourceType.GIT_SOURCE, "clone"] # for backward compatibility, to remove in the future

    @property
    def is_local_source(self) -> bool:
        return self.source_type == SourceType.LOCAL_FILE
