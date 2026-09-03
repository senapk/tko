from __future__ import annotations

from pathlib import Path
from tko.game.task import Task
from tko.game.task_location import TaskLocation
from tko.game.task_enums import EvalMode
from tko.repository.git_cache import GitCache


class TaskResolver:
    def __init__(self, git_cache: GitCache, repo_root_dir: Path):
        self.git_cache = git_cache
        self.remote_root_dir = repo_root_dir

    def __source_work_dir(self, task: Task) -> Path:
        key_path = Path(task.basic.key)
        if key_path.parts and key_path.parts[0] == task.basic.source_name:
            source_root = self.remote_root_dir
            relative_key = Path(*key_path.parts[1:])
        else:
            source_root = self.remote_root_dir / task.basic.source_name
            relative_key = key_path

        if len(relative_key.parts) == 1:
            canonical = source_root / "labs" / relative_key
            legacy = source_root / relative_key
        elif relative_key.parts[0] == "labs":
            canonical = source_root / relative_key
            legacy = source_root / Path(*relative_key.parts[1:])
        else:
            canonical = source_root / relative_key
            legacy = None

        if canonical.exists():
            return canonical
        if legacy is not None and legacy.exists():
            return legacy
        return canonical

    def target_folder(self, task: Task) -> Path | None:
        file = self.target_file(task)
        if file is None:
            return None
        return file.parent

    def target_file(self, task: Task) -> Path | None:
        loc = task.location

        match loc.eval:
            case EvalMode.NONE:
                if loc.is_external:
                    return self.__source_work_dir(task) / "README.md"
                return None
            case EvalMode.SELF | EvalMode.DIFF:
                # if is git url, is import type
                if loc.is_external:
                    return self.__source_work_dir(task) / "README.md"
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
