from tko.game.task import Task
from tko.run.run_context import RunContext


class TaskResolutionService:
    @staticmethod
    def try_setup_task_from_repo(ctx: RunContext) -> bool:
        if ctx.repo is None:
            return False
        task = ctx.repo.get_task_from_task_folder(ctx.pwd)
        if task is not None:
            ctx.task = task
        return True

    @staticmethod
    def setup_task_from_wdir(ctx: RunContext) -> bool:
        if ctx.task is not None:
            return False
        if not ctx.wdir_builded:
            return False
        task = Task()
        task.basic.key = "STANDALONE"
        task.basic.remote_name = "NONE"
        ctx.task = task
        ctx.track_folder = None
        return True

    def setup_task(self, ctx: RunContext):
        self.try_setup_task_from_repo(ctx)
        if ctx.task is None:
            self.setup_task_from_wdir(ctx)