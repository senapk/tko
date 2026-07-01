from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tko.util.git_hub_url import GitHubUrl
from typing import Any
from loguru import logger

class Keys:
    NAME = "name"
    PATH_OR_URL = "path_or_url"
    WRITEABLE = "writeable"
    TYPE = "type"

    TARGET = "target"
    INDEX = "index"
    QUESTS = "quests"
    TASKS = "tasks"
    BRANCH = "branch"

class SourceType(Enum):
    LOCAL_FILE = "local"
    GIT_SOURCE = "git"

"""
name: str - unique identifier for the source, used to reference the source in the code and configuration
path_or_url: str - for LOCAL_FILE, it's file path; for GIT_SOURCE, it's the git file blob URL
source_type: SourceType - type of the source, either LOCAL_FILE or GIT_SOURCE
writeable: bool - indicates if the source is writeable, used to determine if the source can be modified or not
"""

DEFAULT_BRANCH = "main"
DEFAULT_INDEX = "README.md"

@dataclass(frozen=True, slots=True)
class Remote:
    source_type: SourceType = SourceType.LOCAL_FILE
    is_editable: bool = False
    
    name: str = ""
    path_or_url: str = ""

    @staticmethod
    def from_local_file(name: str, target: Path, is_editable: bool = False) -> Remote:
        if target.is_dir():
            target = target / DEFAULT_INDEX
        return Remote(
            name=name,
            source_type=SourceType.LOCAL_FILE,
            is_editable=is_editable,
            path_or_url=target.as_posix(),
        )

    @staticmethod
    def from_git_file(name: str, target: str, branch: str | None = None, index: str | None = None) -> Remote | None:
        gus = GitHubUrl.parse(target)
        if gus is None:
            logger.warning(f"Invalid GitHub URL: {target}")
            return None
        target = gus.repository_url
        if branch is not None:
            gus = gus.set_branch(branch)
        if index is not None:
            gus = gus.set_relative_path(index)
        if gus.relative_path is None:
            gus = gus.set_relative_path(DEFAULT_INDEX)
        return Remote(
            name=name,
            source_type=SourceType.GIT_SOURCE,
            is_editable=False,
            path_or_url=gus.blob_url
        )
        

    @property
    def is_git_source(self) -> bool:
        return self.source_type == SourceType.GIT_SOURCE

    @property
    def is_local_source(self) -> bool:
        return self.source_type == SourceType.LOCAL_FILE

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Remote:
        name: str = ""
        target: str = ""
        path_or_url: str | None = None
        is_editable: bool = False
        index: str = DEFAULT_INDEX
        source_type: SourceType = SourceType.LOCAL_FILE

        if Keys.NAME in data and isinstance(data[Keys.NAME], str):
            name = data[Keys.NAME]
        if Keys.PATH_OR_URL in data and isinstance(data[Keys.PATH_OR_URL], str):
            path_or_url = data[Keys.PATH_OR_URL]
        if Keys.WRITEABLE in data and isinstance(data[Keys.WRITEABLE], bool):
            is_editable = data[Keys.WRITEABLE]



        if "alias" in data and isinstance(data["alias"], str): # for backward compatibility
            name = data["alias"]
        if "database" in data and isinstance(data["database"], str): # for backward compatibility
            name = data["database"]
        if Keys.TARGET in data and isinstance(data[Keys.TARGET], str):
            target = data[Keys.TARGET]
        if Keys.BRANCH in data and isinstance(data[Keys.BRANCH], str):
            branch = data[Keys.BRANCH]
        else:
            branch = "main"
        if Keys.TYPE in data and isinstance(data[Keys.TYPE], str):
            type_str = data[Keys.TYPE]
            if type_str == SourceType.LOCAL_FILE.value:
                source_type = SourceType.LOCAL_FILE
            else:
                source_type = SourceType.GIT_SOURCE
        else:
            source_type = SourceType.LOCAL_FILE
        if name == "sandbox": # for backward compatibility, to remove in the future
            is_editable = True
        if Keys.INDEX in data and isinstance(data[Keys.INDEX], str):
            index = data[Keys.INDEX]
        else:
            index = "README.md"


        if source_type == SourceType.GIT_SOURCE:
            if path_or_url is not None:
                remote = Remote.from_git_file(name=name, target=path_or_url, branch=None, index=None)
            else:
                remote = Remote.from_git_file(name=name, target=target, branch=branch, index=index)
            if remote is None:
                raise ValueError(f"Invalid git source: {target}")
            return remote
        else:
            if path_or_url is not None:
                return Remote.from_local_file(name=name, target=Path(path_or_url), is_editable=is_editable)
            else:
                return Remote.from_local_file(name=name, target=Path(target) / index, is_editable=is_editable)

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {
            Keys.NAME: self.name,
            Keys.TYPE: self.source_type.value,
            Keys.WRITEABLE: self.is_editable,
            Keys.PATH_OR_URL: self.path_or_url,
        }
        return output