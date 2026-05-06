import curses
from typing import Callable

from tko.config.app_settings import ToggleOption
from tko.config.settings import Settings
from tko.game.task import Task
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.widget.border import Border
from tko.floating.floating import Floating
from tko.floating.floating_manager import FloatingManager
from tko.widget.fmt import Fmt
from tko.play.input_manager import InputManager
from tko.play.keys import GuiKeys
from tko.play.opener import Opener
from tko.tester.tester_executor import TesterExecutor
from tko.tester.tester_navigator import TesterNavigator
from tko.tester.tester_palette import TesterPalette
from tko.tester.tester_renderer import TesterRenderer
from tko.tester.tester_state import TesterState, SeqMode
from tko.tester.tester_top_bar import TesterTopBar
from tko.tester import tester_util
from tko.repository.repository import Repository
from tko.run.solver_builder import CompileError
from tko.run.wdir import Wdir


class Tester:

    def __init__(self, settings: Settings, rep: Repository | None, wdir: Wdir, task: Task) -> None:
        self.settings = settings
        self.rep = rep
        self.wdir = wdir
        self.task = task
        self.app = settings.app

        borders = Border(settings.app)
        fman    = FloatingManager()

        self.state    = TesterState(list(wdir.get_unit_list()))
        self.top_bar  = TesterTopBar(wdir, task, borders, settings.app)
        self.executor = TesterExecutor(settings, rep, wdir, task, fman, self.top_bar)
        self.renderer = TesterRenderer(settings, wdir, task, borders, self.top_bar, None)
        self.navigator = TesterNavigator(settings, rep, wdir, task, fman, self.executor)
        self.palette   = TesterPalette(settings.app, fman, self.navigator)
        self.fman = fman

        if rep:
                rep.logger.store(
                    LogItemMove().set_mode(LogItemMove.Mode.PICK).set_key(task.identity.get_full_key())
            )

    def set_opener(self, opener: Opener) -> "Tester":
        opener_with_fman = opener.set_fman(self.fman)
        self.renderer.set_opener(opener_with_fman)
        self.navigator_opener = opener_with_fman
        return self

    def set_autorun(self, value: bool) -> "Tester":
        if value:
            self.state.mode = SeqMode.running
        return self

    def set_exit(self) -> "Tester":
        self.state.exit = True
        return self

    # ------------------------------------------------------------------
    # Despacho de teclas (orquestra todos os sub-componentes)
    # ------------------------------------------------------------------

    def _process_key(self, key: int) -> Callable[[], bool] | None:
        state = self.state
        nav   = self.navigator

        if key == ord('q'):
            self.set_exit()
        elif key == curses.KEY_EXIT:
            if state.locked_index:
                state.locked_index = False
            else:
                self.set_exit()
        elif key == curses.KEY_LEFT:
            nav.go_left(state)
        elif key == curses.KEY_RIGHT:
            nav.go_right(state)
        elif key == curses.KEY_DOWN:
            nav.go_down(state)
        elif key == curses.KEY_UP:
            nav.go_up(state)
        elif key == ord(GuiKeys.toggle_main):
            nav.change_main(state)
        elif key == ord(GuiKeys.execute) or key == curses.KEY_BACKSPACE:
            return self.executor.run_exec_mode(state)
        elif key == ord(GuiKeys.evaluate) or key == ord('\n'):
            self.executor.run_test_mode(state)
        elif key == ord(GuiKeys.lock):
            self.fman.add_input(
                Floating().bottom().right().set_warning()
                .put_text("Função de travamento {}".format("ligada" if not state.locked_index else "desligada"))
            )
            nav.lock_unit(state)
        elif key == ord(GuiKeys.edit):
            opener = getattr(self, "navigator_opener", None)
            if opener is not None:
                opener.open_files()
        elif key == ord(GuiKeys.self_evaluate):
            nav.self_evaluate(state)
        elif key == ord(GuiKeys.limite):
            nav.change_limit(state)
            self.fman.add_input(
                Floating().bottom().right().set_warning()
                .put_text("Limite de execução alterado para {}".format(
                    tester_util.get_time_limit_symbol(self.settings.app.timeout)
                ))
            )
            self.settings.save_settings()
        elif key == ord(GuiKeys.diff):
            self.app.toggle_diff()
            self.fman.add_input(
                Floating().bottom().right().set_warning()
                .put_text("Modo de Diff alterado para {}".format(self.app.diff_mode))
            )
            self.settings.save_settings()
        elif key == ord(GuiKeys.borders):
            self.app.toggle(ToggleOption.BORDERS)
            self.fman.add_input(
                Floating().bottom().right().set_warning()
                .put_text("Modo de Bordas alterado para {}".format(
                    "ligado" if self.app.use_borders else "desligado"
                ))
            )
            self.settings.save_settings()
        elif key == ord(GuiKeys.images):
            self.app.toggle(ToggleOption.IMAGES)
            self.fman.add_input(
                Floating().bottom().right().set_warning()
                .put_text("Modo de Imagens alterado para {}".format(
                    "ligado" if self.app.use_images else "desligado"
                ))
            )
            self.settings.save_settings()
        elif key == ord(GuiKeys.palette):
            self.palette.open(state)
        elif key != -1 and key != curses.KEY_RESIZE:
            self.fman.add_input(
                Floating().bottom().right().set_error()
                .put_text(f"Tecla char:{chr(key)}, code:{key}, não reconhecida")
            )
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
                        self.fman.add_input(
                            Floating().bottom().right().set_error().put_text(e.message)
                        )
                        state.mode = SeqMode.finished
                    Fmt.clear()
                    self.top_bar.draw(state)
                    self.renderer.show_bottom_line(state)
                    Fmt.refresh()
                self.executor.process_one(state)

            self.renderer.draw(state)

            if self.fman.has_floating():
                self.fman.draw_warnings()

            if state.mode == SeqMode.running:
                Fmt.refresh()
                continue

            if self.fman.has_floating():
                self.fman.draw()

            value = InputManager.get_and_remap_keys(scr, self.app)
            if self.fman.has_floating():
                value = self.fman.process_input(value)

            fn_exec = self._process_key(value)
            if fn_exec is not None:
                return fn_exec  # type: ignore[return-value]
        return None

    def run(self) -> None:
        while True:
            free_run_fn = curses.wrapper(self.main)  # type: ignore[arg-type]
            if free_run_fn is None:
                if self.rep:
                    self.rep.logger.store(
                        LogItemMove()
                        .set_mode(LogItemMove.Mode.BACK)
                            .set_key(self.task.identity.get_full_key())
                    )
                break
            else:
                while True:
                    try:
                        repeat = free_run_fn()
                        if not repeat:
                            break
                    except CompileError as e:
                        self.state.mode = SeqMode.finished
                        if self.rep:
                            self.rep.logger.store(
                                LogItemExec()
                                    .set_key(self.task.identity.get_full_key())
                                .set_mode(LogItemExec.Mode.FREE)
                                .set_fail(LogItemExec.Fail.COMP)
                            )
                        print(e)
                        input("Pressione enter para continuar")
                        break
