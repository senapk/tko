from tko.config.app_settings import AppSettings
from tko.game.task import Task
from tko.widget.border import Border
from tko.widget.frame import Frame
from tko.play.keys import GuiActions, GuiKeys
from tko.tester.tester_state import TesterState, SeqMode
from tko.tester import tester_util
from tko.run.unit import Unit
from tko.run.wdir import Wdir
from tko.util.rtext import RText
from tko.util.symbols import Symbols
from tko.enums.execution_result import ExecutionResult
from tko.i18n import Msg, t


class _TesterTopBarMsg:
    RUNNING_LOCKED_ACTIVITY = Msg(pt="Executando atividade travada", en="Running locked activity")
    NO_TESTS_REGISTERED = Msg(pt="Nenhum teste cadastrado", en="No tests registered")
    COMPILE_ERROR = Msg(pt="Erro de compilação", en="Compilation error")


class TesterTopBar:

    def __init__(self, wdir: Wdir, task: Task, borders: Border, app: AppSettings) -> None:
        self.wdir = wdir
        self.task = task
        self.borders = borders
        self.app = app
        self._dummy_unit = Unit()

    def get_fixed_arrow(self, state: TesterState) -> RText:
        diff_text = tester_util.get_diff_symbol(self.app.diff_mode)
        output = RText(f" {GuiKeys.diff} {diff_text} ", "B")
        color = "R" if state.locked_index else "G"
        if self.app.use_borders:
            output += RText(Symbols.sharp_right, color + "b")
        else:
            output += RText(" ", "B")
        symbol = Symbols.locked_locked if state.locked_index else Symbols.locked_free
        output += RText(f" {GuiKeys.lock} {symbol} ", color) + self.borders.sharp_r(color)
        return output

    def build_top_line_header(self, state: TesterState, frame_dx: int) -> RText:
        activity_color = "C"
        solver_color   = "X"
        sources_color  = "Y"
        running_color  = "R"

        folder   = tester_util.get_folder(self.task)
        activity = self.borders.border(activity_color, folder.name)

        solver_names = tester_util.get_solver_names(self.wdir)
        solvers = RText()
        if len(solver_names) > 1:
            solvers += self.borders.round_l("R") + RText(f"{GuiActions.tab}", "R") + self.borders.sharp_r("R")
        for i, solver in enumerate(solver_names):
            if len(solver_names) > 1:
                solvers += " "
            color = "G" if i == self.task.main_idx else solver_color
            solvers += self.borders.border(color, solver)

        done = len(state.results)
        full = len(self.wdir.get_unit_list())
        count_missing = self.borders.border(running_color, f"({done}/{full})")
        if state.mode == SeqMode.running:
            if state.locked_index:
                solvers = self.borders.border("R", t(_TesterTopBarMsg.RUNNING_LOCKED_ACTIVITY))
            else:
                solvers = count_missing

        source_names = RText.join(
            [RText(f"{name[0]}({name[1]})", sources_color) for name in self.wdir.sources_names()],
            RText(", ")
        )
        if self.wdir.has_tests():
            sources = self.borders.round_l(sources_color) + source_names + self.borders.round_r(sources_color)
        else:
            sources = self.borders.border("R", t(_TesterTopBarMsg.NO_TESTS_REGISTERED))

        delta = frame_dx - solvers.len()
        left, right = 1, 1
        if delta > 0:
            delta_left = delta // 2
            left  = max(1, delta_left - activity.len())
            right = max(1, (delta - delta_left) - sources.len())
        filler = "─" if self.wdir.has_tests() else " "
        return activity + filler * left + solvers + filler * right + sources

    def build_unit_list(self, state: TesterState, frame: Frame) -> RText:
        done_list = state.results
        if len(done_list) > 0 and state.locked_index:
            _, index = done_list[state.focused_index]
            done_list[state.focused_index] = (
                state.get_focused_unit(self.wdir, self._dummy_unit).result,
                index,
            )

        todo_list: list[tuple[ExecutionResult, int]] = []
        i = len(done_list)
        for _ in state.unit_list:
            if state.locked_index and i == state.focused_index:
                todo_list.append((self.wdir.get_unit(state.focused_index).result, i))
            else:
                todo_list.append((ExecutionResult.UNTESTED, i))
            i += 1

        show_focused = (
            not self.wdir.get_solver().has_compile_error()
            and state.mode != SeqMode.intro
            and not state.is_all_right()
        )

        output = self.get_fixed_arrow(state)
        i = 0
        for unit_result, index in done_list + todo_list:
            foco = i == state.focused_index
            token = tester_util.get_token(unit_result)
            token_style = token.runs[0][0] if token.runs else ""
            token_text  = token.plain()
            extrap = self.borders.round_l(token_style)
            extras = self.borders.round_r(token_style)
            if foco and show_focused:
                extrap = RText("(")
                extras = RText(")")
            if state.locked_index and not foco:
                output += "  " + RText(str(index).zfill(2), token_style.lower()) + RText(token_text, token_style.lower()) + " "
            else:
                output += " " + extrap + RText(str(index).zfill(2), token_style) + token + extras
            i += 1

        size     = 6
        to_remove = 0
        dx       = frame.get_dx()
        while (state.focused_index + 4) * size - to_remove >= dx:
            to_remove += size
        output = output.slice(0, 3 * 6) + output.slice(3 * 6 + to_remove)
        return output

    def draw_top_bar_content(self, state: TesterState, frame: Frame) -> None:
        if not self.wdir.has_tests():
            return
        unit = state.get_focused_unit(self.wdir, self._dummy_unit)
        info = RText()
        if self.wdir.get_solver().has_compile_error():
            info = self.borders.border("R", t(_TesterTopBarMsg.COMPILE_ERROR))
        elif not state.is_all_right() and state.mode != SeqMode.intro:
            info = unit.str(pad=False)
        frame.write(0, 0, info.center(frame.get_dx()))

    def draw(self, state: TesterState) -> None:
        from tko.widget.fmt import Fmt
        _, cols = Fmt.get_size()
        size = 3 if self.wdir.has_tests() else 1
        frame = Frame(0, 0).set_size(size, cols)
        if not self.wdir.has_tests():
            frame.set_border_none()
        frame.set_header(self.build_top_line_header(state, frame.get_dx()))
        self.draw_top_bar_content(state, frame)
        frame.set_footer(self.build_unit_list(state, frame), "")
        frame.draw()
