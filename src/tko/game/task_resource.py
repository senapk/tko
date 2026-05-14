from __future__ import annotations
from pathlib import Path
import enum

class ResourceType(enum.Enum):
    VIEW = "view"  # md_file, url, pdf or other resource link, not editable
    EDIT = "task"  # editable task
    UNKNOWN = "unknown"

class TaskResource:
    def __init__(self):
        self.raw_link: str = ""
        self.line_number: int = 0
        self.line_data: str = ""
        
        self.external_url: str | None = None # view task to an external link, can be a url or a absolute file path
        self.resource_type: ResourceType = ResourceType.UNKNOWN
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
        new_location.resource_type = self.resource_type
        new_location.remote_git = self.remote_git
        new_location.remote_dir = self.remote_dir
        new_location.relative_path = self.relative_path
        new_location.editable_source = self.editable_source
        return new_location
        
    @property
    def is_view(self) -> bool:
        return self.resource_type == ResourceType.VIEW
    
    @property
    def is_edit(self) -> bool:
        return self.resource_type == ResourceType.EDIT
    
    @property
    def is_link(self) -> bool:
        return self.external_url is not None
        
    @property
    def is_static_type(self) -> bool:
        return self.resource_type == ResourceType.EDIT and self.editable_source

    @property
    def is_import_type(self) -> bool:
        return self.resource_type == ResourceType.EDIT and not self.editable_source