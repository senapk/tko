from typing import Callable

from tko.config.settings import Settings
from tko.game.task import Task
from tko.floating.floating_manager import FloatingManager
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
        fman: FloatingManager,
        top_bar: TesterTopBar,
    ) -> None:
        self.settings = settings
        self.rep = rep
        self.wdir = wdir
        self.task = task
        self.fman = fman
        self.top_bar = top_bar
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
        track_folder = self.rep.paths.get_track_task_folder(self.task.basic.full_key)
        tracker = Tracker()
        tracker.set_folder(track_folder)
        tracker.set_files(self.wdir.get_solver().args_list)
        tracker.set_result(result)
        return tracker.store()

    def process_one(self, state: TesterState) -> None:
        self.execution_service.process_one(state)

    def run_test_mode(self, state: TesterState) -> None:
        self.run_mode_service.run_test_mode(state)

    def run_exec_mode(self, state: TesterState) -> Callable[[], bool]:
        return self.run_mode_service.run_exec_mode(state)
