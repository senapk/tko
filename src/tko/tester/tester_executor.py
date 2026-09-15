from typing import Callable

from tko.config.settings import Settings
from tko.game.task import Task
from tko.tester.tester_state import TesterState
from tko.tester.tester_top_bar import TesterTopBar
from tko.tester.tester_execution_service import TesterExecutionService
from tko.tester.tester_run_mode_service import TesterRunModeService
from tko.repository.repository import Repository
from tko.run.wdir import Wdir
from tko.logger.tracker import Tracker


class TesterExecutor:

    def __init__(
        self,
        settings: Settings,
        rep: Repository | None,
        wdir: Wdir,
        task: Task,
        top_bar: TesterTopBar,
        on_warning: Callable[[str], None] | None = None,
    ) -> None:
        self.settings = settings
        self.rep = rep
        self.wdir = wdir
        self.task = task
        self.top_bar = top_bar
        self.tracker: Tracker = Tracker(on_warning=on_warning)
        self.execution_service = TesterExecutionService(
            settings=settings,
            rep=rep,
            wdir=wdir,
            task=task,
            store_version=self.store_version,
        )
        self.run_mode_service = TesterRunModeService(
            settings=settings,
            rep=rep,
            wdir=wdir,
            task=task,
            top_bar=top_bar,
            store_version=self.store_version,
        )

    def store_version(self, result: str) -> tuple[bool, int]:
        if self.rep is None:
            return False, 0
        history_folder = self.rep.paths.get_history_task_folder(self.task.basic.full_key)
        self.tracker.set_folder(history_folder / "files")
        self.tracker.set_event_folder(history_folder)
        self.tracker.set_event_type("execution")
        task_root = self.rep.task_resolver.target_folder(self.task)
        if task_root is not None:
            self.tracker.set_task_root(task_root)
        if not self.wdir.solver:
            return False, 0
        self.tracker.set_files(self.wdir.solver.args_list)
        self.tracker.set_result(result)
        return self.tracker.store()

    def process_one(self, state: TesterState) -> None:
        self.execution_service.process_one(state)

    def run_test_mode(self, state: TesterState) -> None:
        self.run_mode_service.run_test_mode(state)

    def run_exec_mode(self, state: TesterState) -> Callable[[], bool]:
        return self.run_mode_service.run_exec_mode(state)
