from __future__ import annotations
from loguru import logger
import curses
from typing import Callable

from tko.config.settings import Settings
from tko.game.task import Task
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove, LogItemMoveMode
from tko.floating.floating import Floating, AlignY, AlignX, Position
from tko.floating.floating_manager import FloatingManager, FloatingWriter
from tko.repository.repository_watcher import RepositoryWatcher
from tko.widget.fmt import Fmt
from tko.play.input_manager import InputManager
from tko.play.gui_keys import GuiKeys
from tko.play.opener import Opener
from tko.tester.tester_executor import TesterExecutor
from tko.tester.tester_navigator import TesterNavigator
from tko.tester.tester_palette import TesterPalette
from tko.tester.tester_renderer import TesterRenderer
from tko.tester.tester_state import TesterState, SeqMode
from tko.tester.tester_top_bar import TesterTopBar
from tko.tester.tester_ui_actions import TesterUiActions
from tko.repository.repository import Repository
from tko.run.solver_builder import CompileError
from tko.run.wdir import Wdir
from tko.i18n import Msg
from tko.util.console import Console




_TESTER_COMPILE_ERROR_DURING_RUN = Msg(
    pt="CompileError durante execução do tester",
    en="CompileError during tester run",
)
_TESTER_PRESS_ENTER_TO_CONTINUE = Msg(
    pt="Pressione enter para continuar",
    en="Press Enter to continue",
)


class Tester:

    def __init__(self, settings: Settings, repo: Repository | None, wdir: Wdir, task: Task, watcher: RepositoryWatcher | None) -> None:
        self.settings = settings
        self.watcher = watcher
        self.rep = repo
        self.wdir = wdir
        self.task = task
        self.app = settings.app
        self.fman = FloatingManager()
        fman = self.fman
        self.state    = TesterState(list(wdir.unit_list))
        edit_mode_fn = lambda: self.watcher is not None and self.watcher.edit_logger is not None
        audit_mode_fn = lambda: self.watcher is not None and self.watcher.audit_logger is not None
        self.top_bar  = TesterTopBar(wdir, task, settings.app, edit_fn=edit_mode_fn, audit_fn=audit_mode_fn)
        self.executor = TesterExecutor(settings, repo, wdir, task, fman, self.top_bar)
        self.renderer = TesterRenderer(settings=settings, wdir=wdir, task=task, fman=fman, top_bar=self.top_bar, opener=None)
        self.navigator = TesterNavigator(settings, repo, wdir, task, fman, self.executor)
        self.palette   = TesterPalette(settings.app, fman, self.navigator)
        self.ui_actions = TesterUiActions(settings, fman, self.navigator, self.palette)

        if repo:
                repo.logger.store(
                    LogItemMove().set_mode(LogItemMoveMode.PICK).set_key(task.basic.full_key)
            )

    def set_opener(self, opener: Opener) -> Tester:
        opener_with_fman = opener.set_fman(self.fman)
        self.renderer.set_opener(opener_with_fman)
        self.navigator_opener = opener_with_fman
        return self

    def set_autorun(self, value: bool) -> Tester:
        if value:
            self.state.mode = SeqMode.running
        return self

    def set_exit(self) -> Tester:
        self.state.exit = True
        return self

    def _process_key_exit(self):
        if self.state.locked_index:
            self.state.locked_index = False
            return
        self.set_exit()

    def _set_exit_void(self):
        self.set_exit()

    def make_callback(self) -> InputManager:
        cman = InputManager()
        state = self.state
        nav = self.navigator

        cman.add_str('q', self._set_exit_void)
        cman.add_int(curses.KEY_EXIT, self._process_key_exit)
        cman.add_int(curses.KEY_LEFT, lambda: nav.go_left(state))
        cman.add_int(curses.KEY_RIGHT, lambda: nav.go_right(state))
        cman.add_int(curses.KEY_DOWN, lambda: nav.go_down(state))
        cman.add_int(curses.KEY_UP, lambda: nav.go_up(state))

        cman.add_str(GuiKeys.toggle_main, lambda: nav.change_main(state))
        cman.add_str(GuiKeys.evaluate, lambda: self.executor.run_test_mode(state))
        cman.add_str('\n', lambda: self.executor.run_test_mode(state))
        cman.add_str(GuiKeys.lock, lambda: self.ui_actions.toggle_lock(state))
        cman.add_str(GuiKeys.edit, lambda: self.ui_actions.open_editor(getattr(self, "navigator_opener", None)))
        cman.add_str(GuiKeys.self_evaluate, lambda: nav.self_evaluate(state))
        cman.add_str(GuiKeys.limite, lambda: self.ui_actions.change_limit(state))
        cman.add_str(GuiKeys.diff, self.ui_actions.toggle_diff)
        cman.add_str(GuiKeys.images, self.ui_actions.toggle_images)
        cman.add_str(GuiKeys.palette, lambda: self.ui_actions.open_palette(state))

        return cman

    # ------------------------------------------------------------------
    # Despacho de teclas (orquestra todos os sub-componentes)
    # ------------------------------------------------------------------

    def _process_key(self, key: int) -> Callable[[], bool] | None:
        if key == ord(GuiKeys.execute) or key == curses.KEY_BACKSPACE:
            return self.executor.run_exec_mode(self.state)

        cman = self.make_callback()
        if cman.has_int_key(key):
            cman.exec_call(key)
            return None
        if key != -1 and key != curses.KEY_RESIZE:
            self.ui_actions.send_char_not_found(key)
        return None

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def main(self, scr: curses.window) -> Callable[[], bool] | None:
        InputManager.fix_esc_delay()
        curses.curs_set(0)
        Fmt.init_colors()
        Fmt.set_scr(scr)

        state = self.state
        while not state.exit:
            Fmt.clear()
            if state.mode == SeqMode.running:
                if self.wdir.get_solver().not_compiled():
                    self.top_bar.draw(state)
                    self.renderer.show_bottom_line(state)
                    self.renderer.show_compilling()
                    Fmt.refresh()
                    try:
                        self.wdir.get_solver().prepare_exec()
                    except CompileError as e:
                        self.fman.add_floating(
                            Floating().bottom().right().set_error().put_text(e.message)
                        )
                        state.mode = SeqMode.finished
                    Fmt.clear()
                    self.top_bar.draw(state)
                    self.renderer.show_bottom_line(state)
                    Fmt.refresh()
                self.executor.process_one(state)

            self.renderer.draw(state)

            if self.fman.has_floatings():
                self.fman.draw_floatings()

            if state.mode == SeqMode.running:
                Fmt.refresh()
                continue

            if self.fman.has_floatings():
                self.fman.draw()

            value = InputManager.get_and_remap_keys(scr, self.app)
            if self.fman.has_floatings():
                value = self.fman.process_input(value)

            fn_exec = self._process_key(value)
            if fn_exec is not None:
                return fn_exec  # type: ignore[return-value]
        return None

    def run(self) -> None:
        while True:
            writer = FloatingWriter(self.fman, Position(AlignY.bottom, AlignX.right, offset_x=-2, offset_y=-2))
            with Console.redirect( stdout = writer, stderr = writer):
                free_run_fn = curses.wrapper(self.main)  # type: ignore[arg-type]
            if free_run_fn is None:
                if self.rep:
                    self.rep.logger.store(
                        LogItemMove()
                        .set_mode(LogItemMoveMode.BACK)
                            .set_key(self.task.basic.full_key)
                    )
                break
            else:
                while True:
                    try:
                        repeat = free_run_fn() 
                        if not repeat:
                            break
                    except CompileError:
                        self.state.mode = SeqMode.finished
                        if self.rep:
                            self.rep.logger.store(
                                LogItemExec()
                                    .set_key(self.task.basic.full_key)
                                    .set_mode(LogItemExec.Mode.FREE)
                                    .set_fail(LogItemExec.Fail.COMP)
                            )
                        logger.exception(str(_TESTER_COMPILE_ERROR_DURING_RUN))
                        input(str(_TESTER_PRESS_ENTER_TO_CONTINUE))
                        break
