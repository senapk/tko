from __future__ import annotations

from loguru import logger

from tko.config.settings import Settings
from tko.game.task import Task
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove, LogItemMoveMode
from tko.play.opener import Opener
from tko.repository.repository import Repository
from tko.repository.repository_watcher import RepositoryWatcher
from tko.run.solver_builder import CompileError
from tko.run.wdir import Wdir


class Tester:
    """Execution entry point backed by the Textual tester screen."""

    def __init__(
        self,
        settings: Settings,
        repo: Repository | None,
        wdir: Wdir,
        task: Task,
        watcher: RepositoryWatcher | None,
    ) -> None:
        self.settings = settings
        self.repo = repo
        self.wdir = wdir
        self.task = task
        self.watcher = watcher
        self._opener: Opener | None = None
        self._autorun = False
        self._exit = False

        if repo:
            repo.logger.store(LogItemMove().set_mode(LogItemMoveMode.PICK).set_key(task.basic.full_key))

    def set_opener(self, opener: Opener) -> Tester:
        self._opener = opener
        return self

    def set_autorun(self, value: bool) -> Tester:
        self._autorun = value
        return self

    def set_exit(self) -> Tester:
        self._exit = True
        return self

    def run(self) -> None:
        from tko.ui_textual import TkoTesterApp

        while not self._exit:
            free_run_fn = TkoTesterApp(
                settings=self.settings,
                repo=self.repo,
                wdir=self.wdir,
                task=self.task,
                watcher=self.watcher,
                opener=self._opener,
                autorun=self._autorun,
            ).run()
            self._autorun = False
            if free_run_fn is None:
                if self.repo:
                    self.repo.logger.store(LogItemMove().set_mode(LogItemMoveMode.BACK).set_key(self.task.basic.full_key))
                return
            try:
                if not free_run_fn():
                    return
            except CompileError:
                if self.repo:
                    self.repo.logger.store(
                        LogItemExec()
                        .set_key(self.task.basic.full_key)
                        .set_mode(LogItemExec.Mode.FREE)
                        .set_fail(LogItemExec.Fail.COMP)
                    )
                logger.exception("CompileError during free execution")
                return
