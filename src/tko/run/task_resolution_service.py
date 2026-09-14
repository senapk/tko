from pathlib import Path
from typing import Protocol

from tko.game.task import Task


class TrackPaths(Protocol):
    def get_track_task_folder(self, label: str) -> Path: ...


class TaskRepository(Protocol):
    @property
    def paths(self) -> TrackPaths: ...

    def get_task_from_task_folder(self, folder: Path) -> Task | None: ...


class TaskResolutionContext(Protocol):
    task: Task | None
    track_folder: Path | None

    @property
    def repo(self) -> TaskRepository | None: ...

    @property
    def pwd(self) -> Path: ...

    @property
    def wdir_builded(self) -> bool: ...


class TaskResolutionService:
    @staticmethod
    def try_setup_task_from_repo(ctx: TaskResolutionContext) -> bool:
        if ctx.repo is None:
            return False
        if ctx.task is None:
            ctx.task = ctx.repo.get_task_from_task_folder(ctx.pwd)
        return True

    @staticmethod
    def setup_task_from_wdir(ctx: TaskResolutionContext) -> bool:
        if ctx.task is not None:
            return False
        if not ctx.wdir_builded:
            return False
        task = Task()
        task.basic.key = "STANDALONE"
        task.basic.source_name = "NONE"
        ctx.task = task
        ctx.track_folder = None
        return True

    def setup_task(self, ctx: TaskResolutionContext) -> None:
        self.try_setup_task_from_repo(ctx)
        if ctx.task is None:
            self.setup_task_from_wdir(ctx)
        elif ctx.repo is not None and ctx.task.basic.full_key != "NONE@STANDALONE":
            ctx.track_folder = ctx.repo.paths.get_track_task_folder(ctx.task.basic.full_key)
