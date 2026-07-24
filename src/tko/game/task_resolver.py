from __future__ import annotations

from pathlib import Path
from tko.game.task import Task
from tko.game.task_location import TaskLocation
from tko.game.task_enums import TaskType
from tko.repository.git_cache import GitCache


class TaskResolver:
    def __init__(self, git_cache: GitCache, repo_root_dir: Path):
        self.git_cache = git_cache
        self.remote_root_dir = repo_root_dir

    def __remote_work_dir(self, task: Task) -> Path:
        return self.remote_root_dir / task.basic.remote_name / task.basic.key

    def target_folder(self, task: Task) -> Path | None:
        file = self.target_file(task)
        if file is None:
            return None
        return file.parent

    def target_file(self, task: Task) -> Path | None:
        loc = task.location

        match (loc.task_type):
            case TaskType.NULL:
                return None
            case TaskType.READ:
                return None
            case TaskType.MAKE:        
                # if is git url, is import type
                if loc.remote_import or loc.is_task_from_git:
                    return self.__remote_work_dir(task) / "README.md"
                else:
                    return self.__calc_origin_file(loc)

    def __calc_origin_file(self, loc: TaskLocation) -> Path:
        index_path: Path = loc.index_path
        raw_link: str = loc.raw_link
        return (index_path.parent / raw_link).resolve()

    def origin_file(self, task: Task, load_git: bool) -> Path | None:
        loc = task.location
        if loc.git_hub_url is not None:
            path, ok = self.git_cache.git_hub_url_to_path(loc.git_hub_url, load_git)
            if ok:
                return path
            else:
                return None
        else:
            return self.__calc_origin_file(loc)
        