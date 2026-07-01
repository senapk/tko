from __future__ import annotations
from dataclasses import dataclass
from tko.util.git_hub_url import GitHubUrl
from pathlib import Path
from tko.game.task_enums import TaskType

@dataclass(frozen=True, slots=True)
class TaskLocation:
    index_path: Path = Path()
    raw_link: str = ""
    line_number: int = 0
    line_data: str = ""
    task_type: TaskType = TaskType.NULL
    git_hub_url: GitHubUrl | None = None
    remote_import: bool = False
        
    def clone(self) -> TaskLocation:
        return TaskLocation(
            index_path=self.index_path,
            raw_link=self.raw_link,
            line_number=self.line_number,
            line_data=self.line_data,
            task_type=self.task_type,
            git_hub_url=self.git_hub_url,
            remote_import=self.remote_import
        )
            
    @property
    def is_read(self) -> bool:
        return self.task_type == TaskType.READ
    
    @property
    def is_make(self) -> bool:
        return self.task_type == TaskType.MAKE
    
    @property
    def is_http_link(self) -> bool:
        return self.raw_link.startswith("http://") or self.raw_link.startswith("https://")

    @property
    def is_read_http_link(self) -> bool:
        return self.task_type == TaskType.READ and self.is_http_link
        
    @property
    def is_task_from_git(self) -> bool:
        return self.git_hub_url is not None

    @property
    def is_static_type(self) -> bool:
        return self.task_type == TaskType.MAKE and not self.is_import_type

    @property
    def is_import_type(self) -> bool:
        return self.task_type == TaskType.MAKE and (self.remote_import or self.is_task_from_git)