import curses
import enum
import os
from typing import List, Optional, Tuple

from tko.game.task import Task
from tko.play.border import Border
from tko.play.flags import Flags
from tko.play.floating import Floating
from tko.play.floating_manager import FloatingManager
from tko.play.fmt import Fmt
from tko.play.frame import Frame
from tko.play.images import compilling, executing, images, intro, random_get, success
from tko.play.keys import GuiActions, GuiKeys, GuiKeys
from tko.play.opener import Opener
from tko.run.diff_builder import DiffBuilder
from tko.util.report import Report
from tko.run.solver_builder import CompileError
from tko.run.unit import Unit
from tko.run.unit_runner import UnitRunner
from tko.run.wdir import Wdir
from tko.settings.settings import Settings
from tko.util.consts import ExecutionResult, Success
from tko.util.freerun import Free
from tko.util.sentence import RToken, Sentence, Token
from tko.util.symbols import symbols
from tko.util.consts import DiffMode
from tko.play.input_manager import InputManager


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
        self.init = 1000   # index of first line to show
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
            info = Sentence().addf(color, line).center(dx - 2, Token(" ", " "))
            if clear:
                Fmt.write(i + init_y, 1, Sentence(" " * info.len()))
            else:
                Fmt.write(i + init_y, 1, Sentence().addf(color, line).center(dx - 2, Token(" ", " ")))

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

    def draw_scrollbar(self):
        y_init = 3
        # if len(self.results_fail) == 0:
        #     return
        tr = "╮"
        br = "╯"
        vbar = "│"
        bar = []

        if self.length > self.space:
            total = self.space
            _begin = False
            _end = False
            if self.init == 0:
                _begin = True
            if self.init == self.length - self.space:
                _end = True

            pre = int((self.init / self.length) * total)
            mid = int((self.space / self.length) * total)
            pos = (max(0, total - pre - mid))

            if _begin:
                pre -= 1
            if _end:
                pos -= 1

            if self.init > 0 and pre == 0:
                pre = 1
                pos -= 1

            if _begin:
                bar.append(tr)
            for _ in range(pre):
                bar.append(vbar)
            for _ in range(mid):
                bar.append("┃")
            for _ in range(pos):
                bar.append(vbar)
            if _end:
                bar.append(br)

        else:
            bar.append(tr)
            for i in range(self.length - 2):
                bar.append(vbar)
            bar.append(br)


        _, cols = Fmt.get_size()
        for i in range(len(bar)):
            Fmt.write(i + y_init, cols - 1, Sentence().add(bar[i]))

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
            self.task.test_progress = (len(success) * 100) // len(self.wdir.get_unit_list())
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


    def build_top_line_header(self, frame):
        activity_color = "C"
        solver_color = "W"
        sources_color = "Y"
        running_color = "R"

        # building activity
        activity = Sentence().add(self.borders.border(activity_color, self.get_folder()))

        # building solvers
        solvers = Sentence()
        if len(self.get_solver_names()) > 1:
            solvers.add(Sentence().add(self.borders.roundL("R")).addf("R", f"{GuiActions.tab}").add(self.borders.sharpR("R")))
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
        count_missing = Sentence().add(self.borders.border(running_color, f"({done}/{full})"))
        if self.mode == SeqMode.running:
            if  self.locked_index:
                solvers = Sentence().add(self.borders.border("R", "Executando atividade travada"))
            else:
                solvers = count_missing

        # building sources
        source_names = Sentence(", ").join([Sentence().addf(sources_color, f"{name[0]}({name[1]})") for name in self.wdir.sources_names()])
        sources = Sentence().add(self.borders.roundL(sources_color)).add(source_names).add(self.borders.roundR(sources_color))

        # merging activity, solvers and sources in header
        delta = frame.get_dx() - solvers.len()
        left = 1
        right = 1
        if delta > 0:
            delta_left = delta // 2
            left = max(1, delta_left - activity.len())
            delta_right = delta - delta_left
            right = max(1, delta_right - sources.len())

        return Sentence().add(activity).add("─" * left).add(solvers).add("─" * right).add(sources)

    def build_unit_list(self, frame: Frame) -> Sentence:
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
        
        output = Sentence()
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
        while (index + 2) * size - to_remove >= dx:
            to_remove += size
        output.data = output.data[:6] + output.data[6 + to_remove:]
        return output

    def get_fixed_arrow(self) -> Sentence:
        free = symbols.locked_free.text
        locked = symbols.locked_locked.text
        symbol = locked if self.locked_index else free
        color = "R" if self.locked_index else "G"
        return Sentence().add(self.borders.roundL(color)).addf(color, f"{GuiKeys.travar} {symbol}").add(self.borders.sharpR(color))

    def draw_top_bar_content(self, frame):
        if not self.wdir.has_tests():
            return
        value = self.get_focused_unit()
        info = Sentence()
        if self.wdir.get_solver().compile_error:
            info = self.borders.border("R", "Erro de compilação")
        elif value is not None and not self.is_all_right() and not self.mode == SeqMode.intro:
            info = value.str(pad = False)
            # if self.locked_index:
            #     info = self.borders.border(focused_unit_color, info.get_text())
        frame.write(0, 0, Sentence().add(info).center(frame.get_dx()))

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
        return cols < Sentence(" ").join(self.make_bottom_line()).len() + 2

    def make_bottom_line(self) -> List[Sentence]:
        cmds: List[Sentence] = []
        if self.app.has_full_hud():
            # rodar
            cmds.append(self.borders.border("M", f"{GuiActions.rodar} [{GuiKeys.rodar}]"))
            # fixar
            color = "G" if self.locked_index else "M"
            symbol = symbols.success if self.locked_index else symbols.failure
            travar = f"{symbol.text} {GuiActions.fixar}[{GuiKeys.travar}]"
            cmds.append(self.borders.border(color, travar))
        # sair
        cmds.append(self.borders.border("C", f" {GuiActions.sair}  [{GuiKeys.sair}]"))
        # editar
        if self.opener is not None:
            cmds.append(self.borders.border("C", f"{GuiActions.editar} [{GuiKeys.editar}]"))
        # ativar
        cmds.append(self.borders.border("G", f"{GuiActions.ativar} [↲]"))
        
        # hud
        color = "G" if self.app.has_full_hud() else "Y"
        symbol = symbols.success if self.app.has_full_hud() else symbols.failure
        cmds.append(self.borders.border(color, f" {symbol.text} {GuiActions.hud} [{GuiKeys.hud}]"))

        if self.app.has_full_hud():
            # tempo
            value = str(self.settings.app.get_timeout())
            if value == "0":
                value = symbols.infinity.text
            cmds.append(
                Sentence()
                    .add(self.borders.roundL("M"))
                    .add(RToken("M", "{} {}[{}]".format(GuiActions.tempo, value, GuiKeys.tempo)))
                    .add(self.borders.roundR("M"))
            )
            # diff mode
            if self.settings.app.get_diff_mode() == DiffMode.DOWN:
                text = f"Diff ⇕ [{GuiKeys.diff}]"
            else:
                text = f"Diff ⇔ [{GuiKeys.diff}]"

            cmds.append(self.borders.border("M", text))
            
        return cmds

    def show_bottom_line(self):
        lines, cols = Fmt.get_size()
        if self.two_column_mode():
            line = self.make_bottom_line()
            one = line[0:2] + line[-2:]
            two = line[2:-2]
            Fmt.write(lines - 2, 0, Sentence(" ").join(one).center(cols, Token(" ")))
            Fmt.write(lines - 1, 0, Sentence(" ").join(two).center(cols, Token(" ")))
        else:
            out = Sentence(" ").join(self.make_bottom_line())
            # if Fmt.get_size()[1] % 2 == 0:
            #     out.add("-")
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
        frame = Frame(2, -1).set_inner(self.space, cols - 1).set_border_square()

        if self.is_all_right():
            self.show_success()
            return
        Report.set_terminal_size(cols)
        
        if self.wdir.get_solver().compile_error:
            received = self.wdir.get_solver().error_msg
            line_list = [Sentence().add(line) for line in received.split("\n")]
        elif self.settings.app.get_diff_mode() == DiffMode.DOWN or not self.wdir.has_tests():
            line_list = DiffBuilder.mount_up_down_diff(unit, curses=True)
        else:
            line_list = DiffBuilder.mount_side_by_side_diff(unit, curses=True)

        self.length = max(1, len(line_list))

        if self.length - self.init < self.space:
            self.init = max(0, self.length - self.space)

        if self.init >= self.length:
            self.init = self.length - 1

        if self.init < self.length:
            line_list = line_list[self.init:]
        for i, line in enumerate(line_list):
            frame.write(i, 0, Sentence().add(line))

        self.draw_scrollbar()
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
            self.fman.add_input(Floating("v>").warning().put_text("←\nAtividade travada\nAperte {} para destravar".format(GuiKeys.travar)))
            return
        if not self.wdir.get_solver().compile_error:
            self.focused_index = max(0, self.focused_index - 1)
            self.init = 1000

    def go_right(self):
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
            self.focused_index = 0
            return
        if self.mode == SeqMode.finished:
            self.mode = SeqMode.select
        if self.locked_index:
            self.fman.add_input(Floating("v>").warning().put_text("→\nAtividade travada\nAperte {} para destravar".format(GuiKeys.travar)))
            return
        if not self.wdir.get_solver().compile_error:
            self.focused_index = min(len(self.wdir.get_unit_list()) - 1, self.focused_index + 1)
            self.init = 1000

    def go_down(self):
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
        self.init += 1

    def go_up(self):
        if self.mode == SeqMode.intro:
            self.mode = SeqMode.select
        self.init = max(0, self.init - 1)

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
            self.fman.add_input(
                Floating("v>").warning()
                .put_text("Atividade travada")
                .put_sentence(Sentence("Aperte ").addf("g", GuiKeys.travar).add(" para destravar"))
                .put_sentence(Sentence("Use ").addf("g", "Enter").add(" para rodar os testes"))
            )

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
            nome = "∞" if valor == 0 else str(valor)
            self.fman.add_input(
                Floating("v>").warning()
                .put_text("Limite de tempo de execução alterado para")
                .put_text(f"{nome} segundos")
            )

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
        elif key == ord(GuiKeys.principal):
            self.change_main()
        elif key == ord(GuiKeys.rodar):
            return self.run_exec_mode()
        elif key == ord(GuiKeys.testar):
            self.run_test_mode()
        elif key == ord(GuiKeys.travar):
            self.lock_unit()
        elif key == ord(GuiKeys.editar):
            if self.opener is not None:
                self.opener.load_folders_and_open()
        elif key == ord(GuiKeys.tempo):
            self.change_limit()
        elif key == ord(GuiKeys.hud):
            self.settings.app.toggle_hud()
            self.settings.save_settings()
        elif key == ord(GuiKeys.diff):
            self.settings.app.toggle_diff()
            self.settings.save_settings()
        elif key == ord(GuiKeys.border):
            self.settings.app.toggle_borders()
            self.settings.save_settings()
        elif key == ord(GuiKeys.images):
            self.settings.app.toggle_images()
            self.settings.save_settings()
        elif key != -1 and key != curses.KEY_RESIZE:
            self.send_char_not_found(key)

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
                        print(e)
                        input("Pressione enter para continuar")
                        break
