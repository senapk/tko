from tko.config.settings import Settings
from tko.game.task import Task
from tko.logger.log_item_self import LogItemSelf
from tko.floating.floating import Floating
from tko.floating.floating_grade import FloatingGrade
from tko.floating.floating_manager import FloatingManager
from tko.play.gui_keys import GuiKeys
from tko.tester.tester_executor import TesterExecutor
from tko.tester.tester_state import TesterState, SeqMode
from tko.tester import tester_util
from tko.repository.repository import Repository
from tko.run.wdir import Wdir
from tko.i18n import Msg, t


class _TesterNavigatorMsg:
    LOCKED_HINT = Msg(
        pt="{arrow}\nAtividade travada\nAperte {lock_key} para destravar",
        en="{arrow}\nLocked activity\nPress {lock_key} to unlock",
    )
    SINGLE_SOLVER_1 = Msg(
        pt="Seu projeto só tem um arquivo de solução.",
        en="Your project has only one solution file.",
    )
    SINGLE_SOLVER_2 = Msg(
        pt="Essa funcionalidade troca qual dos arquivos",
        en="This feature switches which solution file",
    )
    SINGLE_SOLVER_3 = Msg(
        pt="de solução será o principal.",
        en="will be used as the main one.",
    )
    NO_LOG_REPO = Msg(
        pt="Nenhum repositório de logs encontrado.",
        en="No log repository found.",
    )


class TesterNavigator:

    def __init__(
        self,
        settings: Settings,
        rep: Repository | None,
        wdir: Wdir,
        task: Task,
        fman: FloatingManager,
        executor: TesterExecutor,
    ) -> None:
        self.settings = settings
        self.rep = rep
        self.wdir = wdir
        self.task = task
        self.fman = fman
        self.executor = executor

    # ------------------------------------------------------------------
    # Navegação de diff / unidades
    # ------------------------------------------------------------------

    def go_left(self, state: TesterState) -> None:
        if state.mode in (SeqMode.intro, SeqMode.finished):
            state.mode = SeqMode.select
        if state.locked_index:
            self.fman.add_input(
                Floating().bottom().right().set_warning().set_countdown(Floating.Time.FAST)
                .put_text(t(_TesterNavigatorMsg.LOCKED_HINT, arrow="←", lock_key=GuiKeys.lock))
            )
            return
        
        if not self.wdir.get_solver().has_compile_error():
            state.focused_index = max(0, state.focused_index - 1)
            state.diff_first_line = 1000

    def go_right(self, state: TesterState) -> None:
        if state.mode == SeqMode.intro:
            state.mode = SeqMode.select
            state.focused_index = 0
            return
        if state.mode == SeqMode.finished:
            state.mode = SeqMode.select
        if state.locked_index:
            self.fman.add_input(
                Floating().bottom().right().set_warning().set_countdown(Floating.Time.FAST)
                .put_text(t(_TesterNavigatorMsg.LOCKED_HINT, arrow="→", lock_key=GuiKeys.lock))
            )
            return
        if not self.wdir.get_solver().has_compile_error():
            state.focused_index = min(
                len(self.wdir.unit_list) - 1,
                state.focused_index + 1,
            )
            state.diff_first_line = 1000

    def go_down(self, state: TesterState) -> None:
        if state.mode == SeqMode.intro:
            state.mode = SeqMode.select
        state.diff_first_line += 1

    def go_up(self, state: TesterState) -> None:
        if state.mode == SeqMode.intro:
            state.mode = SeqMode.select
        state.diff_first_line = max(0, state.diff_first_line - 1)

    # ------------------------------------------------------------------
    # Ações de controle
    # ------------------------------------------------------------------

    def change_main(self, state: TesterState) -> None:
        solver_names = tester_util.get_solver_names(self.wdir)
        if len(solver_names) == 1:
            self.fman.add_input(
                Floating().bottom().right().set_warning().set_countdown(Floating.Time.MEDIUM)
                .put_text(t(_TesterNavigatorMsg.SINGLE_SOLVER_1))
                .put_text(t(_TesterNavigatorMsg.SINGLE_SOLVER_2))
                .put_text(t(_TesterNavigatorMsg.SINGLE_SOLVER_3))
            )
            return
        self.task.main_idx = (self.task.main_idx + 1) % len(solver_names)

    def lock_unit(self, state: TesterState) -> None:
        state.locked_index = not state.locked_index
        if state.mode == SeqMode.intro:
            state.mode = SeqMode.select
        if state.locked_index:
            for i in range(len(state.results)):
                _, index = state.results[i]
                from tko.enums.execution_result import ExecutionResult
                state.results[i] = (ExecutionResult.UNTESTED, index)

    def change_limit(self, state: TesterState) -> None:
        valor = self.settings.app.timeout
        valor = 1 if valor == 0 else valor * 2
        if valor >= 5:
            valor = 0
        self.settings.app.timeout = valor
        self.settings.save_settings()

    def self_evaluate(self, state: TesterState) -> None:
        if self.rep is None:
            self.fman.add_input(
                Floating().bottom().right().set_warning().set_countdown(Floating.Time.MEDIUM)
                .put_text(t(_TesterNavigatorMsg.NO_LOG_REPO))
            )
            return
        logger = self.rep.logger
        self.fman.add_input(
            FloatingGrade(self.task, lambda task: logger.store(LogItemSelf().set_task(task)))
        )
