from tko.config.settings import Settings
from tko.enums.diff_mode import DiffMode
from tko.game.task import Task
from tko.widget.fmt import Fmt
from tko.widget.frame import Frame
from tko.play.images import compilling_image, executing_image, images, intro, random_get, success_image
from tko.play.keys import GuiActions, GuiKeys
from tko.play.opener import Opener
from tko.tester.tester_state import TesterState, SeqMode
from tko.tester.tester_top_bar import TesterTopBar
from tko.tester import tester_util
from tko.run.diff_builder import DiffBuilder
from tko.run.diff_builder_down import DiffBuilderDown
from tko.run.diff_builder_side import DiffBuilderSide
from tko.run.unit import Unit
from tko.run.wdir import Wdir
from tko.util.rtext import RText
from tko.util.symbols import Symbols


class TesterRenderer:

    def __init__(
        self,
        settings: Settings,
        wdir: Wdir,
        task: Task,
        top_bar: TesterTopBar,
        opener: Opener | None,
    ) -> None:
        self.settings = settings
        self.wdir = wdir
        self.task = task
        self.top_bar = top_bar
        self.opener = opener
        self._dummy_unit = Unit()

    def set_opener(self, opener: Opener) -> None:
        self.opener = opener

    # ------------------------------------------------------------------
    # Imagens / animações
    # ------------------------------------------------------------------

    @staticmethod
    def print_centered_image(image: str, color: str, clear: bool = False, align: str = ".") -> None:
        dy, dx = Fmt.get_size()
        lines = image.splitlines()[1:]
        init_y = 4
        if align == "v":
            init_y = dy - len(lines) - 1
        for i, line in enumerate(lines):
            info = RText(line, color).center(dx - 2, " ")
            if clear:
                Fmt.write(i + init_y, 1, RText(" " * info.len()))
            else:
                Fmt.write(i + init_y, 1, info)

    def show_success(self) -> None:
        folder = str(tester_util.get_folder(self.task).name)
        if self.settings.app.use_images:
            out = random_get(images, folder, "static")
        else:
            out = random_get(success_image, folder, "static")
        TesterRenderer.print_centered_image(out, "g")

    def show_compilling(self, clear: bool = False) -> None:
        folder = str(tester_util.get_folder(self.task).name)
        out = random_get(compilling_image, folder, "random")
        TesterRenderer.print_centered_image(out, "y", clear)

    @staticmethod
    def show_executing(clear: bool = False) -> None:
        TesterRenderer.print_centered_image(executing_image, "y", clear, "v")

    # ------------------------------------------------------------------
    # Barras
    # ------------------------------------------------------------------

    def border(self, color: str, text: str) -> RText:
        return RText(f" {text} ", color)

    def make_bottom_line(self, state: TesterState) -> list[RText]:
        cmds: list[RText] = []
        cmds.append(self.border("C", f"{GuiActions.goback}"))
        cmds.append(self.border("C", f"{GuiActions.pallete} [{GuiKeys.palette}]"))
        if self.opener is not None:
            cmds.append(self.border("C", f"{GuiActions.edit} [{GuiKeys.edit}]"))
        cmds.append(self.border("G", f"{GuiActions.evaluate_tester} [{GuiKeys.evaluate} | {Symbols.newline}]"))
        cmds.append(self.border("G", f"{GuiActions.execute_tester} [{GuiKeys.execute} | ←]"))
        limite = f"{GuiActions.time_limit} {tester_util.get_time_limit_symbol(self.settings.app.timeout)} [{GuiKeys.limite}]"
        cmds.append(self.border("Y", limite))
        return cmds

    def show_bottom_line(self, state: TesterState) -> None:
        lines, cols = Fmt.get_size()
        out = RText.join(self.make_bottom_line(state), RText(" "))
        Fmt.write(lines - 1, 0, out.center(cols, " "))

    # ------------------------------------------------------------------
    # Área principal (diff)
    # ------------------------------------------------------------------

    def draw_main(self, state: TesterState) -> None:
        unit = state.get_focused_unit(self.wdir, self._dummy_unit)
        lines, cols = Fmt.get_size()
        if self.wdir.has_tests():
            y_out = 2
            state.space = lines - 4
        else:
            y_out = 0
            state.space = lines - 2
        frame = Frame(y_out, -1).set_inner(state.space, cols)

        if state.is_all_right():
            self.show_success()
            return

        DiffBuilder(cols).set_curses()

        if self.wdir.get_solver().has_compile_error():
            executable, _ = self.wdir.get_solver().get_executable()
            received = executable.get_error_msg().get_str()
            line_list = [RText(line) for line in received.splitlines()]
        elif self.settings.app.diff_mode == DiffMode.DOWN or not self.wdir.has_tests():
            line_list = DiffBuilderDown(cols, unit).build_diff()
        else:
            line_list = DiffBuilderSide(cols, unit).build_diff()

        state.length = max(1, len(line_list))

        if state.length - state.diff_first_line < state.space:
            state.diff_first_line = max(0, state.length - state.space)
        if state.diff_first_line >= state.length:
            state.diff_first_line = state.length - 1
        if state.diff_first_line < state.length:
            line_list = line_list[state.diff_first_line:]
        for i, line in enumerate(line_list):
            frame.write(i, 0, line)

    # ------------------------------------------------------------------
    # Ponto de entrada de renderização de um frame completo
    # ------------------------------------------------------------------

    def draw(self, state: TesterState) -> None:
        self.top_bar.draw(state)
        if state.mode == SeqMode.intro:
            folder = str(tester_util.get_folder(self.task).name)
            TesterRenderer.print_centered_image(random_get(intro, folder), "y")
        else:
            self.draw_main(state)
        self.show_bottom_line(state)
