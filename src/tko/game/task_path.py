from __future__ import annotations

from pathlib import Path
from tko.game.task_resource import TaskResource
from tko.game.task_resource import ResourceType
from tko.repository.git_cache import GitCache
from tko.game.tree_item import TreeBasic
from tko.i18n import Msg, t


_TASK_PATH_VIEW_NO_WORKDIR = Msg(
    pt="Task {task_key} is a view resource, it does not have a work directory",
    en="Task {task_key} is a view resource, it does not have a work directory",
)
_TASK_PATH_INVALID_LOCAL_PATH = Msg(
    pt="Task {task_key} does not have a valid local path",
    en="Task {task_key} does not have a valid local path",
)

class TaskPath:
    def __init__(self, git_cache: GitCache, remote_root_dir: Path, loc: TaskResource, basic: TreeBasic):
        self.git_cache = git_cache
        self.remote_root_dir = remote_root_dir
        self.loc = loc
        self.basic = basic

    @property
    def work_dir(self) -> Path | None:
        loc = self.loc
        if loc.resource_type == ResourceType.VIEW:
            raise ValueError(t(_TASK_PATH_VIEW_NO_WORKDIR, task_key=self.basic.full_key))
        if loc.editable_source:
            target = self.__remote_local_path(loc)
            if target is None:
                raise ValueError(t(_TASK_PATH_INVALID_LOCAL_PATH, task_key=self.basic.full_key))
            return target.parent
        return self.remote_root_dir / self.basic.remote_name / self.basic.key
    
    def __remote_local_path(self, loc: TaskResource) -> Path | None:
        if loc.remote_dir is None:
            return None
        if loc.relative_path is None:
            return None
        return (loc.remote_dir / loc.relative_path).resolve()

    @property
    def origin_target(self) -> Path | None:
        loc = self.loc
        if loc.remote_git is not None and loc.relative_path is not None:
            git_root_dir = self.git_cache.get_remote_dir(loc.remote_git, verbose=False)
            if git_root_dir is not None:
                return (git_root_dir / loc.relative_path).resolve()
        return self.__remote_local_path(loc)

    def check_origin_path(self) -> bool:
        if self.loc.external_url is not None:
            return True
        target = self.origin_target
        if target is None:
            return False
        return target.exists()