from __future__ import annotations
from pathlib import Path

from tko.game.task_enums import TaskType

class TaskResource:
    def __init__(self):
        self.raw_link: str = ""
        self.line_number: int = 0
        self.line_data: str = ""
        
        self.external_url: str | None = None # read task to an external link, can be a url or a absolute file path
        self.task_type: TaskType = TaskType.NULL
        self.remote_git: str | None = None
        self.remote_dir: Path | None = None
        self.relative_path: Path | None = None
        self.editable_source: bool = False
        
    def clone(self) -> TaskResource:
        new_location = TaskResource()
        new_location.raw_link = self.raw_link
        new_location.line_number = self.line_number
        new_location.line_data = self.line_data
        new_location.external_url = self.external_url
        new_location.task_type = self.task_type
        new_location.remote_git = self.remote_git
        new_location.remote_dir = self.remote_dir
        new_location.relative_path = self.relative_path
        new_location.editable_source = self.editable_source
        return new_location
        
    @property
    def is_read(self) -> bool:
        return self.task_type == TaskType.READ
    
    @property
    def is_make(self) -> bool:
        return self.task_type == TaskType.MAKE
    
    @property
    def is_link(self) -> bool:
        return self.external_url is not None
        
    @property
    def is_static_type(self) -> bool:
        return self.task_type == TaskType.MAKE and self.editable_source

    @property
    def is_import_type(self) -> bool:
        return self.task_type == TaskType.MAKE and not self.editable_source