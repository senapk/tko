from tko.play.opener import Opener
from tko.run.filter_mode_service import FilterModeService
from tko.run.opener_factory import OpenerFactory
from tko.run.run_context import RunContext
from tko.run.task_resolution_service import TaskResolutionService
from tko.run.wdir_bootstrap_service import WdirBootstrapService


class RunLoader:
    def __init__(self, ctx: RunContext):
        self.ctx = ctx
        self.task_resolution = TaskResolutionService()
        self.filter_mode = FilterModeService()
        self.wdir_bootstrap = WdirBootstrapService()
        self.opener_factory = OpenerFactory()

    def setup_task(self):
        self.task_resolution.setup_task(self.ctx)

    def build_wdir(self):
        return self.wdir_bootstrap.build(self.ctx, self.filter_mode)

    def try_setup_task_from_rep(self) -> bool:
        return self.task_resolution.try_setup_task_from_repo(self.ctx)

    def _remove_duplicates(self):
        self.wdir_bootstrap.remove_duplicates(self.ctx)

    def _change_targets_to_filter_mode(self) -> None:
        self.ctx.target_list = self.filter_mode.apply(self.ctx.target_list)

    def setup_task_from_wdir(self) -> bool:
        return self.task_resolution.setup_task_from_wdir(self.ctx)
            
    def create_opener_for_wdir(self) -> Opener:
        return self.opener_factory.create_for_wdir(self.ctx)
