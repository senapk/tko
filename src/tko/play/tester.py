import curses
import enum
import os
from typing import List, Optional, Tuple

from tko.game.task import Task
from tko.play.border import Border
from tko.play.flags import Flags
from tko.play.floating import Floating, FloatingInput, FloatingInputData
from tko.play.floating_manager import FloatingManager
from tko.play.fmt import Fmt
from tko.play.frame import Frame
from tko.play.images import compilling, executing, images, intro, random_get, success
from tko.play.keys import GuiActions, GuiKeys, GuiKeys
from tko.play.opener import Opener
from tko.run.diff_builder import DiffBuilder
from tko.run.solver_builder import CompileError
from tko.run.unit import Unit
from tko.run.unit_runner import UnitRunner
from tko.run.wdir import Wdir
from tko.settings.settings import Settings
from tko.util.consts import ExecutionResult
from tko.util.freerun import Free
from tko.util.text import  Text, Token
from tko.util.symbols import symbols
from tko.util.consts import DiffMode
from tko.play.input_manager import InputManager
from tko.settings.logger import Logger
from tko.run.diff_builder_down import DownDiff
from tko.run.diff_builder_side import SideDiff
from tko.play.tracker import Tracker
from tko.util.raw_terminal import RawTerminal
from tko.settings.repository import Repository


class SeqMode(enum.Enum):
    intro = 0
    select = 1
    running = 2
    finished = 3

class Tester:
    def __init__(self, settings: Settings, rep: Repository | None, wdir: Wdir, task: Task):
        self.results: List[Tuple[ExecutionResult, int]] = []
        self.wdir = wdir
        self.rep: Repository | None = rep
        self.unit_list = [unit for unit in wdir.get_unit_list()] # unit list to be consumed
        self.exit = False
        self.task = task
        self.diff_first_line = 1000   # index of first line to show
        self.length = 1  # length of diff
        self.space = 0  # dy space for draw
        self.mode: SeqMode = SeqMode.intro

        self.settings = settings
        self.app = settings.app
        self.borders = Border(settings.app)

        self.locked_index: bool = False
        self.focused_index = 0
        self.resumes: List[str] = []

        self.fman = FloatingManager()
        self.opener: Optional[Opener] = None
        self.dummy_unit = Unit()

        Logger.get_instance().record_pick(self.task.key)


    def set_opener(self, opener: Opener):
        self.opener = opener
        self.opener.set_fman(self.fman)
        return self

    def set_autorun(self, value:bool):
        if value:
            self.mode = SeqMode.running
        return self

    def set_exit(self):
        self.exit = True
        return self

    def print_centered_image(self, image: str, color: str, clear=False, align: str = "."):
        dy, dx = Fmt.get_size()
        lines = image.splitlines()[1:]
        init_y = 4
        if align == "v":
            init_y = dy - len(lines) - 1
        for i, line in enumerate(lines):
            info = Text().addf(color, line).center(dx - 2, Token(" ", " "))
            if clear:
                Fmt.write(i + init_y, 1, Text().add(" " * info.len()))
            else:
                Fmt.write(i + init_y, 1, Text().addf(color, line).center(dx - 2, Token(" ", " ")))

    def show_success(self):
        if self.settings.app.get_use_images():
            out = random_get(images, self.get_folder(), "static")
        else:
            out = random_get(success, self.get_folder(), "static")
        self.print_centered_image(out, "g")
        
    def show_compilling(self, clear=False):
        out = random_get(compilling, self.get_folder(), "random")
        self.print_centered_image(out, "y", clear)

    def show_executing(self, clear=False):
        out = executing
        self.print_centered_image(out, "y", clear, "v")

    def get_folder(self) -> str:
        folder = self.task.get_folder()
        if folder is None:
            raise Warning("Folder is None")
    
        return os.path.basename(folder)

    def get_focused_unit(self) -> Unit:
        if not self.wdir.has_tests():
            return self.dummy_unit
        if len(self.results) != 0:
            _, index = self.results[self.focused_index]
            unit = self.wdir.get_unit(index)
            return unit
        return self.wdir.get_unit(self.focused_index)

    def get_token(self, result: ExecutionResult) -> Token:
        if result == ExecutionResult.SUCCESS:
            return Token(ExecutionResult.get_symbol(ExecutionResult.SUCCESS).text, "G")
        elif result == ExecutionResult.WRONG_OUTPUT:
            return Token(ExecutionResult.get_symbol(ExecutionResult.WRONG_OUTPUT).text, "R")
        elif result == ExecutionResult.COMPILATION_ERROR:
            return Token(ExecutionResult.get_symbol(ExecutionResult.UNTESTED).text, "W")
        elif result == ExecutionResult.EXECUTION_ERROR:
            return Token(ExecutionResult.get_symbol(ExecutionResult.EXECUTION_ERROR).text, "Y")
        else:
            return Token(ExecutionResult.get_symbol(ExecutionResult.UNTESTED).text, "W")

    def store_test_track(self, result: int):
        if self.rep is None:
            return
        track_folder = self.rep.get_track_task_folder(self.task.key)
        tracker = Tracker()
        tracker.set_folder(track_folder)
        tracker.set_files(self.wdir.get_solver().path_list)
        tracker.set_percentage(result)
        tracker.store()

    def store_other_track(self, result: str | None = None):
        if self.rep is None:
            return
        track_folder = self.rep.get_track_task_folder(self.task.key)
        tracker = Tracker()
        tracker.set_folder(track_folder)
        tracker.set_files(self.wdir.get_solver().path_list)
        if result is not None:
            tracker.set_result(result)
        tracker.store()

    def process_one(self):

        if self.mode != SeqMode.running:
            return

        solver = self.wdir.get_solver()

        if solver.compile_error:
            Logger.get_instance().record_compilation_execution_error(self.task.key)
            self.store_other_track(ExecutionResult.COMPILATION_ERROR.value)

            self.mode = SeqMode.finished
            while len(self.unit_list) > 0:
                index = len(self.results)
                self.unit_list = self.unit_list[1:]
                self.results.append((ExecutionResult.COMPILATION_ERROR, index))
            return
        
        if self.locked_index or not self.wdir.has_tests():
            self.mode = SeqMode.finished
            unit = self.get_focused_unit()
            unit.result = UnitRunner.run_unit(solver, unit, self.settings.app.timeout)
            return

        if self.wdir.has_tests():
            index = len(self.results)
            unit = self.unit_list[0]
            self.unit_list = self.unit_list[1:]
            unit.result = UnitRunner.run_unit(solver, unit, self.settings.app.get_timeout())
            self.results.append((unit.result, index))
            self.focused_index = index

        if len(self.unit_list) == 0:
            self.mode = SeqMode.finished
            self.focused_index = 0

            done_list: List[Tuple[ExecutionResult, int]] = []
            fail_list: List[Tuple[ExecutionResult, int]] = []
            for data in self.results:
                unit_result, _ = data
                if unit_result != ExecutionResult.SUCCESS:
                    fail_list.append(data)
                else:
                    done_list.append(data)
            self.results = fail_list + done_list
            percent: int = (100 * len(done_list)) // len(self.results)
            self.task.coverage = percent
            Logger.get_instance().record_test_result(self.task.key, percent)
            self.store_test_track(percent)


    def build_top_line_header(self, frame_dx):
        activity_color = "C"
        solver_color = "W"
        sources_color = "Y"
        running_color = "R"

        # building activity
        activity = Text().add(self.borders.border(activity_color, self.get_folder()))

        # building solvers
        solvers = Text()
        if len(self.get_solver_names()) > 1:
            solvers.add(Text().add(self.borders.roundL("R")).addf("R", f"{GuiActions.tab}").add(self.borders.sharpR("R")))
        for i, solver in enumerate(self.get_solver_names()):
            if len(self.get_solver_names()) > 1:
                solvers.add(" ")
            color = solver_color
            if i == self.task.main_idx:
                color = "G"
            solvers.add(self.borders.border(color, solver))
        
        # replacing with count if running
        done = len(self.results)
        full = len(self.wdir.get_unit_list())
        count_missing = Text().add(self.borders.border(running_color, f"({done}/{full})"))
        if self.mode == SeqMode.running:
            if  self.locked_index:
                solvers = Text().add(self.borders.border("R", "Executando atividade travada"))
            else:
                solvers = count_missing

        # building sources
        source_names = Text().add(", ").join([Text().addf(sources_color, f"{name[0]}({name[1]})") for name in self.wdir.sources_names()])
        if self.wdir.has_tests():
            sources = Text().add(self.borders.roundL(sources_color)).add(source_names).add(self.borders.roundR(sources_color))
        else:
            sources = Text().add(self.borders.border("R", "Nenhum teste cadastrado"))

        # merging activity, solvers and sources in header
        delta = frame_dx - solvers.len()
        left = 1
        right = 1
        if delta > 0:
            delta_left = delta // 2
            left = max(1, delta_left - activity.len())
            delta_right = delta - delta_left
            right = max(1, delta_right - sources.len())
        filler = "─" if self.wdir.has_tests() else " "
        return Text().add(activity).add(filler * left).add(solvers).add(filler * right).add(sources)

    def build_unit_list(self, frame: Frame) -> Text:
        done_list = self.results
        if len(done_list) > 0 and self.locked_index:
            _, index = done_list[self.focused_index]
            done_list[self.focused_index] = (self.get_focused_unit().result, index)
        todo_list: List[Tuple[ExecutionResult, int]] = []
        i = len(done_list)
        for _ in self.unit_list:
            if self.locked_index and i == self.focused_index:
                todo_list.append((self.wdir.get_unit(self.focused_index).result, i))
            else:
                todo_list.append((ExecutionResult.UNTESTED, i))
            i += 1

        i = 0
        show_focused_index = not self.wdir.get_solver().compile_error and not self.mode == SeqMode.intro and not self.is_all_right()
        
        output = Text()
        output.add(self.get_fixed_arrow())


        for unit_result, index in done_list + todo_list:
            foco = i == self.focused_index
            token = self.get_token(unit_result)
            extrap = self.borders.roundL(token.fmt)
            extras = self.borders.roundR(token.fmt)
            if foco and show_focused_index:
                # token.fmt = token.fmt.lower() + ""
                extrap = Token("(")
                extras = Token(")")
                # extrap = Token(" ") #self.borders.roundL("")
                # extras = Token(" ") #self.borders.roundR("")
            if self.locked_index and not foco:
                output.add("  ").addf(token.fmt.lower(), str(index).zfill(2)).addf(token.fmt.lower(), token.text).add(" ")
            else:
                output.add(" ").add(extrap).addf(token.fmt, str(index).zfill(2)).add(token).add(extras)
            i += 1

        size = 6
        to_remove = 0
        index = self.focused_index
        dx = frame.get_dx()
        while (index + 4) * size - to_remove >= dx:
            to_remove += size
        output.data = output.data[:3 * 6] + output.data[3 * 6 + to_remove:]
        return output

    def get_fixed_arrow(self) -> Text:
        
        output = Text()
        # diff
        diff_text = self.get_diff_symbol()
        output.addf("B", f" {GuiKeys.diff} {diff_text} ")
        # if self.settings.app.has_borders():
        #     output.addf("Mb", symbols.sharpR.text)
        # else:
        #     output.addf("B", " ")
        # timer
        # timer = symbols.timer.text
        # value = str(self.settings.app.get_timeout())
        # if value == "0":
        #     value = symbols.infinity.text
        # output.addf("M", f"{timer}l {value}  ")
        color = "R" if self.locked_index else "G"
        if self.settings.app.get_use_borders():
            output.addf(color + "b", symbols.sharpR.text)
        else:
            output.addf("B", " ")

        # travar
        free = symbols.locked_free.text
        locked = symbols.locked_locked.text
        symbol = locked if self.locked_index else free
        output.addf(color, f" {GuiKeys.lock} {symbol} ").add(self.borders.sharpR(color))

        return output

    def draw_top_bar_content(self, frame):
        if not self.wdir.has_tests():
            return
        value = self.get_focused_unit()
        info = Text()
        if self.wdir.get_solver().compile_error:
            info = self.borders.border("R", "Erro de compilação")
        elif value is not None and not self.is_all_right() and not self.mode == SeqMode.intro:
            info = value.str(pad = False)
            # if self.locked_index:
            #     info = self.borders.border(focused_unit_color, info.get_text())
        frame.write(0, 0, Text().add(info).center(frame.get_dx()))

    def draw_top_bar(self):
        # construir mais uma solução
        _, cols = Fmt.get_size()
        size = 1
        if self.wdir.has_tests():
            size = 3
        frame = Frame(0, 0).set_size(size, cols)
        if not self.wdir.has_tests():        
            frame.set_border_none()
        frame.set_header(self.build_top_line_header(frame.get_dx()))
        self.draw_top_bar_content(frame)
        frame.set_footer(self.build_unit_list(frame), "")
        frame.draw()

    def get_diff_symbol(self) -> str:
        if self.settings.app.get_diff_mode() == DiffMode.DOWN:
            return symbols.diff_down.text
        return symbols.diff_left.text

    def make_bottom_line(self) -> List[Text]:
        cmds: List[Text] = []
        text = f"{GuiActions.config} [{GuiKeys.palette}]"
        cmds.append(self.borders.border("C", text))

        color ="Y"
        limite = f"{GuiActions.time_limit} {self.get_time_limit_symbol()} [{GuiKeys.limite}]"
        cmds.append(self.borders.border(color, limite))

        # ativar
        cmds.append(self.borders.border("G", f"{GuiActions.evaluate_tester} [{symbols.newline.text}]"))
        #editar
        if self.opener is not None:
            cmds.append(self.borders.border("Y", f"{GuiActions.edit} [{GuiKeys.edit}]"))
        # rodar
        cmds.append(self.borders.border("C", f"{GuiActions.execute_tester} [{GuiKeys.execute_tester}]"))
            
        return cmds

    def show_bottom_line(self):
        lines, cols = Fmt.get_size()
        out = Text().add(" ").join(self.make_bottom_line())
        Fmt.write(lines - 1, 0, out.center(cols, Token(" ")))

    def is_all_right(self):
        if self.locked_index or len(self.results) == 0:
            return False
        if not self.mode == SeqMode.finished:
            return False
        for result, _ in self.results:
            if result != ExecutionResult.SUCCESS:
                return False
        return True

    def draw_main(self):
        unit = self.get_focused_unit()
        lines, cols = Fmt.get_size()
        if self.wdir.has_tests():
            y_out = 2
            self.space = lines - 4
        else:
            y_out = 0
            self.space = lines - 2
        frame = Frame(y_out, -1).set_inner(self.space, cols)

        if self.is_all_right():
            self.show_success()
            return
        
        diff_builder = DiffBuilder(cols)
        diff_builder.set_curses()

        if self.wdir.get_solver().compile_error:
            received = self.wdir.get_solver().error_msg
            line_list = [Text().add(line) for line in received.splitlines()]
        elif self.settings.app.get_diff_mode() == DiffMode.DOWN or not self.wdir.has_tests():
            ud_diff = DownDiff(cols, unit)
            line_list = ud_diff.build_diff()
        else:
            ss_diff = SideDiff(cols, unit)
            line_list = ss_diff.build_diff()

        self.length = max(1, len(line_list))

        if self.length - self.diff_first_line < self.space:
            self.diff_first_line = max(0, self.length - self.space)

        if self.diff_first_line >= self.length:
            self.diff_first_line = self.length - 1

        if self.diff_first_line < self.length:
            line_list = line_list[self.diff_first_line:]
        for i, line in enumerate(line_list):
            frame.write(i, 0, Text().add(line))
        return

    def get_solver_names(self):
        return sorted(self.wdir.solvers_names())
    
    def main(self, scr):
        InputManager.fix_esc_delay()
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global
        while not self.exit:

            Fmt.clear()
            if self.mode == SeqMode.running:
                if self.wdir.get_solver().not_compiled():
                    self.draw_top_bar()
                    self.show_bottom_line()
                    self.show_compilling()
                    Fmt.refresh()
                    try:
                        self.wdir.get_solver().prepare_exec()
                    except CompileError as e:
                        self.fman.add_input(Floating("v>").error().put_text(e.message))
                        self.mode = SeqMode.finished
                    Fmt.clear()
                    self.draw_top_bar()
                    self.show_bottom_line()
                    Fmt.refresh()
                self.process_one()
            self.draw_top_bar()

            if self.mode == SeqMode.intro:
                self.print_centered_image(random_get(intro, self.get_folder()), "y")
            else:
                self.draw_main()
            
            self.show_bottom_line()

            if self.fman.has_floating():
                self.fman.draw_warnings()

            if self.mode == SeqMode.running:
                Fmt.refresh()
                continue

            if self.fman.has_floating():
                key = self.fman.get_input()
            else:
                key = Fmt.getch()

            fn_exec = self.process_key(key)
            if fn_exec is not None:
                return fn_exec

    def run_exec_mode(self):
        self.mode = SeqMode.running
        if self.wdir.is_autoload():
            self.wdir.autoload()
            self.wdir.get_solver().set_main(self.get_solver_names()[self.task.main_idx])
        self.mode = SeqMode.finished
        Logger.get_instance().record_freerun(self.task.key)
        self.store_other_track("Execução Livre")
        header = self.build_top_line_header(RawTerminal.get_terminal_size())
        return lambda: Free.free_run(self.wdir.get_solver(), show_compilling=True, to_clear=True, wait_input=True, header=header)

    def run_test_mode(self):
        self.mode = SeqMode.running
        if self.wdir.is_autoload():
            self.wdir.autoload() # reload sources and solvers
        self.wdir.build() # reload cases

        Fmt.clear()

        solver_names = self.get_solver_names()
        solver_size = len(solver_names)
        index = self.task.main_idx
        solver_selected = solver_names[index % solver_size]
        self.wdir.get_solver().set_main(solver_selected).reset() # clear old compilation
        
        if self.locked_index:
            for i in range(len(self.results)):
                _, index = self.results[i]
                self.results[i] = (ExecutionResult.UNTESTED, index)
        else:
            self.focused_index = 0
            self.results = []
            self.unit_list = [unit for unit in self.wdir.get_unit_list()]

    def send_char_not_found(self, key):
        if not Flags.devel:
            return
        self.fman.add_input(Floating("v>").error()
                    .put_text("Tecla")
                    .put_text(f"char {chr(key)}")
                    .put_text(f"code {key}")
                    .put_text("não reconhecida")
                    .put_text("")
                    )

    def go_left(self):
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
        if self.mode == SeqMode.finished:
            self.mode = SeqMode.select
        if self.locked_index:
            self.fman.add_input(Floating("v>").warning().put_text("←\nAtividade travada\nAperte {} para destravar".format(GuiKeys.lock)))
            return
        if not self.wdir.get_solver().compile_error:
            self.focused_index = max(0, self.focused_index - 1)
            self.diff_first_line = 1000

    def go_right(self):
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
            self.focused_index = 0
            return
        if self.mode == SeqMode.finished:
            self.mode = SeqMode.select
        if self.locked_index:
            self.fman.add_input(Floating("v>").warning().put_text("→\nAtividade travada\nAperte {} para destravar".format(GuiKeys.lock)))
            return
        if not self.wdir.get_solver().compile_error:
            self.focused_index = min(len(self.wdir.get_unit_list()) - 1, self.focused_index + 1)
            self.diff_first_line = 1000

    def go_down(self):
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
        self.diff_first_line += 1

    def go_up(self):
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
        self.diff_first_line = max(0, self.diff_first_line - 1)

    def change_main(self):
        if len(self.get_solver_names()) == 1:
            self.fman.add_input(
                Floating("v>").warning()
                .put_text("Seu projeto só tem um arquivo de solução")
                .put_text("Essa funcionalidade troca qual dos arquivos")
                .put_text("de solução será o principal.")
            )
            return
        self.task.main_idx = (self.task.main_idx + 1) % len(self.get_solver_names())

    def lock_unit(self):
        self.locked_index = not self.locked_index
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
        if self.locked_index:
            for i in range(len(self.results)):
                _, index = self.results[i]
                self.results[i] = (ExecutionResult.UNTESTED, index)

    def get_time_limit_symbol(self):
        if self.settings.app.get_timeout() == 0:
            return symbols.infinity.text
        return str(self.settings.app.get_timeout())

    def change_limit(self):
            valor = self.settings.app.get_timeout()
            if valor == 0:
                valor = 1
            else:
                valor *= 2
            if valor >= 5:
                valor = 0
            self.settings.app.set_timeout(valor)
            self.settings.save_settings()


    def process_key(self, key):
        if key == ord('q') or any([key == x for x in InputManager.backspace_list]):
            self.set_exit()
        elif key == InputManager.esc:
            if self.locked_index:
                self.locked_index = False
            else:
                self.set_exit()
        elif any([key == x for x in InputManager.left_list]) or key == ord(GuiKeys.left):
            self.go_left()
        elif any([key == x for x in InputManager.right_list]) or key == ord(GuiKeys.right):
            self.go_right()
        elif key == curses.KEY_DOWN or key == ord(GuiKeys.down):
            self.go_down()
        elif key == curses.KEY_UP or key == ord(GuiKeys.up):
            self.go_up()
        elif key == ord(GuiKeys.toggle_main):
            self.change_main()
        elif key == ord(GuiKeys.execute_tester):
            return self.run_exec_mode()
        elif key == ord(GuiKeys.evaluate):
            self.run_test_mode()
        elif key == ord(GuiKeys.lock):
            self.lock_unit()
        elif key == ord(GuiKeys.edit):
            if self.opener is not None:
                self.opener.load_folders_and_open()
        elif key == ord(GuiKeys.limite):
            self.change_limit()
            self.settings.save_settings()
        elif key == ord(GuiKeys.diff):
            self.settings.app.toggle_diff()
            self.settings.save_settings()
        elif key == ord(GuiKeys.borders):
            self.settings.app.toggle_borders()
            self.settings.save_settings()
        elif key == ord(GuiKeys.images):
            self.settings.app.toggle_images()
            self.settings.save_settings()
        elif key == ord(GuiKeys.palette):
            self.command_pallete()
        elif key != -1 and key != curses.KEY_RESIZE:
            self.send_char_not_found(key)

    def command_pallete(self):
        options: list[FloatingInputData] = []

        def icon(value: bool):
            return "✓" if value else "✗"
        
        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mudar arquivo {y} de execução", symbols.action, "principal"),
                self.change_main,
                "TAB"
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mudar modo {y}}", self.get_diff_symbol(), "Diff"),
                self.app.toggle_diff,
                GuiKeys.diff
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mudar {y} de tempo de execução: {r}", symbols.action, "Limite", self.get_time_limit_symbol()),
                self.change_limit,
                GuiKeys.limite
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Testar {y} os casos ou apenas o selecionado", icon(not self.locked_index), "Todos"),
                self.lock_unit,
                GuiKeys.lock
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", icon(self.app.get_use_borders()), "Bordas"),
                self.app.toggle_borders,
                GuiKeys.borders
            )
        )
        
        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", icon(self.app.get_use_images()), "Imagens"),
                self.app.toggle_images, 
                GuiKeys.images
            )
        )

        self.fman.add_input(
            FloatingInput("v").set_text_ljust()
                      .set_header(" Selecione uma ação da lista ")
                      .set_options(options)
                      .set_exit_on_enter(False)
                      .set_footer(" Use Enter para aplicar e Esc para Sair ")
        )

    def run(self):
        while True:
            free_run_fn = curses.wrapper(self.main)
            if free_run_fn == None:
                Logger.get_instance().record_back(self.task.key)
                break
            else:
                while(True):
                    try:
                        repeat = free_run_fn()
                        if repeat == False:
                            break
                    except CompileError as e:
                        self.mode = SeqMode.finished
                        Logger.get_instance().record_compilation_execution_error(self.task.key)
                        self.store_other_track(ExecutionResult.COMPILATION_ERROR.value)
                        print(e)
                        input("Pressione enter para continuar")
                        break
