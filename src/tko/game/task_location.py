from __future__ import annotations

from pathlib import Path

from tko.game.task_config import TaskEdit


class TaskLocation:
    def __init__(self):
        self.target = ""
        self.line_number = 0
        self.line = ""
        self.__origin_folder: Path | None = None
        self.__workspace_folder: Path | None = None

    def clone(self) -> TaskLocation:
        new_location = TaskLocation()
        new_location.target = self.target
        new_location.line_number = self.line_number
        new_location.line = self.line
        new_location.__origin_folder = self.__origin_folder
        new_location.__workspace_folder = self.__workspace_folder
        return new_location

    def is_folderless(self) -> bool:
        return self.__origin_folder is None and self.__workspace_folder is None

    def is_link(self, task_mode: TaskEdit) -> bool:
        if task_mode == TaskEdit.VIEW:
            return True
        return self.is_folderless()

    def is_import_type(self, task_mode: TaskEdit) -> bool:
        return task_mode == TaskEdit.EDIT and self.__origin_folder is not None and self.__workspace_folder is not None

    def is_static_type(self, task_mode: TaskEdit) -> bool:
        if self.is_link(task_mode):
            return False
        return self.get_origin_folder() == self.get_workspace_folder()

    def set_remote_view_type(self):
        self.__origin_folder = None
        self.__workspace_folder = None
        return self

    def set_origin_folder(self, folder: Path):
        self.__origin_folder = folder.resolve()
        return self

    def get_origin_readme(self) -> Path:
        origin_folder = self.get_origin_folder()
        if origin_folder is not None:
            return origin_folder / "README.md"
        return Path("")

    def set_workspace_folder(self, folder: Path):
        self.__workspace_folder = folder.resolve()
        return self

    def get_origin_folder(self) -> Path | None:
        return self.__origin_folder.resolve() if self.__origin_folder is not None else None

    def get_workspace_folder(self) -> Path | None:
        if self.__workspace_folder is not None:
            return self.__workspace_folder.resolve()
        return self.__origin_folder.resolve() if self.__origin_folder is not None else None
