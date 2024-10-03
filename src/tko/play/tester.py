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
from tko.util.raw_terminal import RawTerminal
from tko.run.solver_builder import CompileError
from tko.run.unit import Unit
from tko.run.unit_runner import UnitRunner
from tko.run.wdir import Wdir
from tko.settings.settings import Settings
from tko.util.consts import ExecutionResult, Success
from tko.util.freerun import Free
from tko.util.text import RToken, Text, Token
from tko.util.symbols import symbols
from tko.util.consts import DiffMode
from tko.play.input_manager import InputManager
from tko.util.logger import LogAction, Logger
from tko.run.diff_builder_down import DownDiff
from tko.run.diff_builder_side import SideDiff


class SeqMode(enum.Enum):
    intro = 0
    select = 1
    running = 2
    finished = 3

class Tester:
    def __init__(self, settings: Settings, wdir: Wdir):
        self.results: List[Tuple[ExecutionResult, int]] = []
        self.wdir = wdir
        self.unit_list = [unit for unit in wdir.get_unit_list()] # unit list to be consumed
        self.exit = False

        self.task = Task()
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


    def set_opener(self, opener: Opener):
        self.opener = opener
        self.opener.set_fman(self.fman)
        return self

    def set_autorun(self, value:bool):
        if value:
            self.mode = SeqMode.running
        return self
    
    def set_task(self, task: Task):
        self.task = task
        return self

    def set_exit(self):
        self.exit = True
        return self

    def print_centered_image(self, image: str, color: str, clear=False, align: str = "."):
        dy, dx = Fmt.get_size()
        lines = image.split("\n")[1:]
        init_y = 4
        if align == "v":
            init_y = dy - len(lines) - 1
        for i, line in enumerate(lines):
            info = Text().addf(color, line).center(dx - 2, Token(" ", " "))
            if clear:
                Fmt.write(i + init_y, 1, Text(" " * info.len()))
            else:
                Fmt.write(i + init_y, 1, Text().addf(color, line).center(dx - 2, Token(" ", " ")))

    def show_success(self):
        if self.settings.app.has_images():
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

    def get_folder(self):
        source_list = self.wdir.get_source_list()
        if source_list:
            folder = os.path.abspath(source_list[0])
        else:
            folder = os.path.abspath(self.wdir.get_solver().path_list[0])
        return folder.split(os.sep)[-2]

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

    def process_one(self):

        if self.mode != SeqMode.running:
            return

        solver = self.wdir.get_solver()

        if solver.compile_error:
            Logger.get_instance().record_event(LogAction.TEST, self.task.key, Logger.COMP_ERROR)
            self.mode = SeqMode.finished
            while len(self.unit_list) > 0:
                index = len(self.results)
                self.unit_list = self.unit_list[1:]
                self.results.append((ExecutionResult.COMPILATION_ERROR, index))
            return
        
        if self.locked_index or not self.wdir.has_tests():
            self.mode = SeqMode.finished
            unit = self.get_focused_unit()
            unit.result = UnitRunner.run_unit(solver, unit, self.settings.app._timeout)
            return

        if self.wdir.has_tests():
            index = len(self.results)
            unit = self.unit_list[0]
            self.unit_list = self.unit_list[1:]
            unit.result = UnitRunner.run_unit(solver, unit, self.settings.app._timeout)
            self.results.append((unit.result, index))
            success = [result for result, _ in self.results if result == ExecutionResult.SUCCESS]
            self.task.progress = (len(success) * 100) // len(self.wdir.get_unit_list())
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
            percent = (100 * len(done_list)) // len(self.results)
            Logger.get_instance().record_event(LogAction.TEST, self.task.key, str(percent) + "%")


    def build_top_line_header(self, frame):
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
            if i == self.task.main_index:
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
        source_names = Text(", ").join([Text().addf(sources_color, f"{name[0]}({name[1]})") for name in self.wdir.sources_names()])
        sources = Text().add(self.borders.roundL(sources_color)).add(source_names).add(self.borders.roundR(sources_color))

        # merging activity, solvers and sources in header
        delta = frame.get_dx() - solvers.len()
        left = 1
        right = 1
        if delta > 0:
            delta_left = delta // 2
            left = max(1, delta_left - activity.len())
            delta_right = delta - delta_left
            right = max(1, delta_right - sources.len())

        return Text().add(activity).add("─" * left).add(solvers).add("─" * right).add(sources)

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
        if self.wdir.has_tests():
            output.add(self.get_fixed_arrow())
        else:
            output.add(self.borders.border("R", "Nenhum teste encontrado"))

        for unit_result, index in done_list + todo_list:
            foco = i == self.focused_index
            token = self.get_token(unit_result)
            extrap = self.borders.roundL(token.fmt)
            extras = self.borders.roundR(token.fmt)
            if foco and show_focused_index:
                token.fmt = token.fmt.lower() + "C"
                extrap = self.borders.roundL("C")
                extras = self.borders.roundR("C")
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
        if self.settings.app.has_borders():
            output.addf("Mb", symbols.sharpR.text)
        else:
            output.addf("B", " ")

        # timer
        timer = symbols.timer.text
        value = str(self.settings.app.get_timeout())
        if value == "0":
            value = symbols.infinity.text
        output.addf("M", f"{timer} {value}  ")
        color = "R" if self.locked_index else "G"
        if self.settings.app.has_borders():
            output.addf(color + "m", symbols.sharpR.text)
        else:
            output.addf("M", " ")

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
        frame = Frame(0, 0).set_size(3, cols)
        frame.set_header(self.build_top_line_header(frame))
        self.draw_top_bar_content(frame)
        frame.set_footer(self.build_unit_list(frame), "")
        frame.draw()
        
    def two_column_mode(self):
        _, cols = Fmt.get_size()
        return cols < Text(" ").join(self.make_bottom_line()).len() + 2

    def get_diff_symbol(self) -> str:
        if self.settings.app.get_diff_mode() == DiffMode.DOWN:
            return symbols.diff_down.text
        return symbols.diff_left.text

    def make_bottom_line(self) -> List[Text]:
        cmds: List[Text] = []

        # diff mode
        # text = f"{self.get_diff_symbol()} Diff [{GuiKeys.diff}]"
        # cmds.append(self.borders.border("C", text))
        # sair
        # cmds.append(self.borders.border("C", f" {GuiActions.sair}  [{GuiKeys.sair}]"))
        # editar
        # tempo
        # value = str(self.settings.app.get_timeout())
        # if value == "0":
        #     value = symbols.infinity.text
        # cmds.append(
        #     Text()
        #         .add(self.borders.roundL("M"))
        #         .add(RToken("M", "{} {}[{}]".format(GuiActions.tempo, value, GuiKeys.tempo)))
        #         .add(self.borders.roundR("M"))
        # )
        # fixar
        color = "R" if self.locked_index else "B"
        symbol = symbols.success if not self.locked_index else symbols.failure
        # name = "Único" if self.locked_index else "Todos"
        travar = f"{symbol.text} {GuiActions.all}[{GuiKeys.lock}]"
        cmds.append(self.borders.border(color, travar))

        text = f"{GuiActions.palette} [{GuiKeys.palette}]"
        cmds.append(self.borders.border("Y", text))
        # ativar
        cmds.append(self.borders.border("G", f"Testar [{symbols.newline.text}]"))
        #editar
        if self.opener is not None:
            cmds.append(self.borders.border("Y", f"{GuiActions.edit} [{GuiKeys.edit}]"))
        # rodar
        cmds.append(self.borders.border("B", f"{GuiActions.interact} [{GuiKeys.interact}]"))



            
        return cmds

    def show_bottom_line(self):
        lines, cols = Fmt.get_size()
        out = Text(" ").join(self.make_bottom_line())
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
        self.space = lines - 4
        if self.two_column_mode():
            self.space = lines - 5
        frame = Frame(2, -1).set_inner(self.space, cols).set_border_square()

        if self.is_all_right():
            self.show_success()
            return
        
        diff_builder = DiffBuilder(cols)
        diff_builder.set_curses()

        if self.wdir.get_solver().compile_error:
            received = self.wdir.get_solver().error_msg
            line_list = [Text().add(line) for line in received.split("\n")]
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
            self.wdir.get_solver().set_main(self.get_solver_names()[self.task.main_index])
        self.mode = SeqMode.finished
        Logger.get_instance().record_event(LogAction.FREE, self.task.key)
        return lambda: Free.free_run(self.wdir.get_solver(), show_compilling=True, to_clear=True, wait_input=True)

    def run_test_mode(self):
        self.mode = SeqMode.running
        if self.wdir.is_autoload():
            self.wdir.autoload() # reload sources and solvers
        
        self.wdir.build() # reload cases

        Fmt.clear()
        self.wdir.get_solver().set_main(self.get_solver_names()[self.task.main_index]).reset() # clear old compilation
        
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
        self.task.main_index = (self.task.main_index + 1) % len(self.get_solver_names())

    def lock_unit(self):
        self.locked_index = not self.locked_index
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
        if self.locked_index:
            for i in range(len(self.results)):
                _, index = self.results[i]
                self.results[i] = (ExecutionResult.UNTESTED, index)
            # self.fman.add_input(
            #     Floating("v>").warning()
            #     .put_text("Atividade travada")
            #     .put_sentence(Text("Aperte ").addf("g", GuiKeys.travar).add(" para destravar"))
            #     .put_sentence(Text("Use ").addf("g", "Enter").add(" para rodar os testes"))
            # )

    def get_time_limit_symbol(self):
        if self.settings.app.get_timeout() == 0:
            return symbols.infinity.text
        return str(self.settings.app.get_timeout())

    def change_limit(self):
            valor = self.settings.app._timeout
            if valor == 0:
                valor = 1
            else:
                valor *= 2
            if valor >= 5:
                valor = 0
            self.settings.app.set_timeout(valor)
            self.settings.save_settings()
            # self.fman.add_input(
            #     Floating("v>").warning()
            #     .put_text("Limite de tempo de execução alterado para")
            #     .put_text(f"{self.get_time_limit_symbol()} segundos")
            # )

    def process_key(self, key):
        if key == ord('q') or key == InputManager.backspace1 or key == InputManager.backspace2:
            self.set_exit()
        elif key == InputManager.esc:
            if self.locked_index:
                self.locked_index = False
            else:
                self.set_exit()
        elif key == curses.KEY_LEFT or key == ord(GuiKeys.left):
            self.go_left()
        elif key == curses.KEY_RIGHT or key == ord(GuiKeys.right):
            self.go_right()
        elif key == curses.KEY_DOWN or key == ord(GuiKeys.down):
            self.go_down()
        elif key == curses.KEY_UP or key == ord(GuiKeys.up):
            self.go_up()
        elif key == ord(GuiKeys.main):
            self.change_main()
        elif key == ord(GuiKeys.interact):
            return self.run_exec_mode()
        elif key == ord(GuiKeys.test):
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
                lambda: Text(" {} Mudar arquivo {y} de execução", symbols.action, "principal"),
                self.change_main,
                "TAB"
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text(" {} Mudar modo {y}}", self.get_diff_symbol(), "Diff"),
                self.app.toggle_diff,
                GuiKeys.diff
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text(" {} Mudar {y} de tempo de execução: {r}", symbols.action, "Limite", self.get_time_limit_symbol()),
                self.change_limit,
                GuiKeys.limite
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text(" {} Testar {y} os casos ou apenas o selecionado", icon(not self.locked_index), "Todos"),
                self.lock_unit,
                GuiKeys.lock
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text(" {} Mostrar {y}", icon(self.app.has_borders()), "Bordas"),
                self.app.toggle_borders,
                GuiKeys.borders
            )
        )
        
        options.append(
            FloatingInputData(
                lambda: Text(" {} Mostrar {y}", icon(self.app.has_images()), "Imagens"),
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
                break
            else:
                while(True):
                    try:
                        repeat = free_run_fn()
                        if repeat == False:
                            break
                    except CompileError as e:
                        self.mode = SeqMode.finished
                        Logger.get_instance().record_event(LogAction.TEST, self.task.key, Logger.COMP_ERROR)
                        print(e)
                        input("Pressione enter para continuar")
                        break
