from tko.run.run_context import RunContext
from tko.logger.tracker import Tracker
from tko.logger.log_item_exec import LogItemExec

class RunTracker:
    def __init__(self, ctx: RunContext):
        self.ctx = ctx

    def store_exec_diff(self, rate: str) -> tuple[bool, int]:
        tracker = Tracker()
        if self.ctx.track_folder is not None:
            tracker.set_folder(self.ctx.track_folder)
            tracker.set_files(self.ctx.wdir.get_solver().args_list)
            tracker.set_result(rate)
            has_changes, total_lines = tracker.store()
            return has_changes, total_lines
        return False, 0

    def store_execution_log(self, rate: int, percent: int, exec_error: bool):
        if self.ctx.task is None or self.ctx.track_folder is None:
            return

        exec_mode = LogItemExec.Mode.FULL if self.ctx.param.index is None else LogItemExec.Mode.LOCK
        exec_fail = LogItemExec.Fail.NONE
        if self.ctx.wdir.get_solver().has_compile_error():
            exec_fail = LogItemExec.Fail.COMP

        changes, size = self.store_exec_diff(str(rate))
        if self.ctx.repo:
            self.ctx.repo.logger.store(LogItemExec()
                .set_mode(exec_mode)
                .set_key(self.ctx.task.get_full_key())
                .set_size(changes, size)
                .set_rate(rate)
                .set_fail(exec_fail))

    def store_free_run_log(self):
        if self.ctx.task is not None and self.ctx.repo:
            changes, size = self.store_exec_diff("---")
            self.ctx.repo.logger.store(LogItemExec()
                .set_mode(LogItemExec.Mode.FREE)
                .set_key(self.ctx.task.get_full_key())
                .set_size(changes, size))
