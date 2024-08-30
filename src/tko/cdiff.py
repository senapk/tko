import curses
from .play.fmt import Fmt
from .run.basic import ExecutionResult
from .run.unit import Unit
from .run.param import Param
from .execution import Execution
from .run.diff import Diff
from .util.sentence import Sentence, Token, RToken
from typing import List, Tuple, Optional
from .play.frame import Frame
from .play.floating import Floating
from .play.floating_manager import FloatingManager
from .play.images import images, compilling, success, intro, executing, random_get
from .util.runner import Runner
from .util.freerun import Free
from .play.style import Style
from .game.task import Task
import random
from .play.opener import Opener
from .run.solver import CompileError
from .play.flags import Flags

from .run.wdir import Wdir
from .run.report import Report
from .settings.settings import Settings
import os
from .run.basic import Success
import enum

class Mode(enum.Enum):
    intro = 0
    select = 1
    running = 2
    finished = 3


class DActions:
    sair   = "  Sair"
    editar = "Editar"
    testar = "Ativar"
    rodar  = " Rodar"
    principal = "Principal"
    fixar  = " Fixar"
    tempo = "Tempo"
    outros = "Outros"

class DKeys:
    backspace1 = 127
    left = "a"
    up = "w"
    right = "d"
    down = "s"
    principal = "p"
    diff = "m"
    rodar = "r"
    testar = "\n"
    # testar2 = "\n"
    sair   = "q"
    editar = "e"
    travar = "f"
    tempo  = "t"
    outros = "o"
    border = "B"

class CDiff:
    def __init__(self, wdir: Wdir, param: Param.Basic, success_type: Success):
        self.param = param
        self.results: List[Tuple[ExecutionResult, int]] = []
        self.wdir = wdir
        self.unit_list = [unit for unit in wdir.get_unit_list()] # unit list to be consumed
        self.exit = False
        self.success_type = success_type
        self.task = Task()
        self.init = 1000   # index of first line to show
        self.length = 1  # length of diff
        self.space = 0  # dy space for draw
        self.mode: Mode = Mode.intro

        self.locked_index: bool = False

        self.focused_index = 0
        self.finished = False
        self.resumes: List[str] = []

        self.settings = Settings()
        self.colors = self.settings.app.is_colored()
        self.first_loop = True
        self.fman = FloatingManager()
        self.first_run = False

        self.opener: Optional[Opener] = None

    def set_first_run(self):
        self.first_run = True
        return self

    def set_opener(self, opener: Opener):
        self.opener = opener
        self.opener.set_fman(self.fman)
        return self

    def set_autorun(self, value:bool):
        if value:
            self.mode = Mode.running
        return self

    def save_settings(self):
        self.settings.app.set_diff_mode("down" if self.param.is_up_down else "side")
        self.settings.save_settings()
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
        init_y = 3
        if align == "v":
            init_y = dy - len(lines) - 1
        for i, line in enumerate(lines):
            info = Sentence().addf(color, line).center(dx - 2, Token(" ", " "))
            if clear:
                Fmt.write(i + init_y, 1, Sentence(" " * info.len()))
            else:
                Fmt.write(i + init_y, 1, Sentence().addf(color, line).center(dx - 2, Token(" ", " ")))

    def show_success(self):
        if self.success_type == Success.RANDOM:
            out = random_get(images, self.get_folder(), "static")
        else:
            out = random_get(success, self.get_folder(), "static")
        self.print_centered_image(out, "" if not self.colors else "g")
        
    def show_compilling(self, clear=False):
        out = random_get(compilling, self.get_folder(), "random")
        self.print_centered_image(out, "" if not self.colors else "y", clear)

    def show_executing(self, clear=False):
        out = executing
        self.print_centered_image(out, "" if not self.colors else "y", clear, "v")

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

        if self.mode != Mode.running:
            return

        solver = self.wdir.get_solver()

        if solver.compile_error:
            self.mode = Mode.finished
            while len(self.unit_list) > 0:
                index = len(self.results)
                self.unit_list = self.unit_list[1:]
                self.results.append((ExecutionResult.COMPILATION_ERROR, index))
            return
        
        if self.locked_index:
            self.mode = Mode.finished
            unit = self.get_focused_unit()
            unit.result = Execution.run_unit(solver, unit, self.settings.app.get_timeout())
            return

        if len(self.unit_list) > 0:
            index = len(self.results)
            unit = self.unit_list[0]
            self.unit_list = self.unit_list[1:]
            unit.result = Execution.run_unit(solver, unit, self.settings.app.get_timeout())
            self.results.append((unit.result, index))
            success = [result for result, _ in self.results if result == ExecutionResult.SUCCESS]
            self.task.test_progress = (len(success) * 100) // len(self.wdir.get_unit_list())
            self.focused_index = index

        if len(self.unit_list) == 0:
            self.mode = Mode.finished
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
        activity_color = "W" if not self.colors else "C"
        solver_color = "W" if not self.colors else "W"
        sources_color = "W" if not self.colors else "Y"
        running_color = "W" if not self.colors else "R"

        # building activity
        activity = Sentence().add(Style.border_round(activity_color, self.get_folder()))

        # building solvers
        solvers = Sentence()
        if len(self.get_solver_names()) > 1:
            solvers.add(Sentence().addf("R", "[p]").add(Style.sharpR("R")))
        for i, solver in enumerate(self.get_solver_names()):
            color = solver_color
            if i == self.task.main_index:
                color = "G"
            solvers.add(Style.border_round(color, solver))
        
        # replacing with count if running
        done = len(self.results)
        full = len(self.wdir.get_unit_list())
        count_missing = Sentence().add(Style.border_round(running_color, f"({done}/{full})"))
        if self.mode == Mode.running:
            if  self.locked_index:
                solvers = Sentence().add(Style.border_round("R", "Executando atividade travada"))
            else:
                solvers = count_missing

        # building sources
        source_names = Sentence(", ").join([Sentence().addf(sources_color, f"{name[0]}({name[1]})") for name in self.wdir.sources_names()])
        sources = Sentence().add(Style.roundL(sources_color)).add(source_names).add(Style.roundR(sources_color))

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

    def build_top_bar_footer(self, frame):
        output = Sentence()
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
        show_focused_index = not self.wdir.get_solver().compile_error and not self.mode == Mode.intro and not self.is_all_right()
        for unit_result, index in done_list + todo_list:
            foco = i == self.focused_index
            token = self.get_token(unit_result)
            extrap = Style.roundL(token.fmt) # if not foco else Token(Style.roundL(), "")
            extras = Style.roundR(token.fmt) # if not foco else Token(Style.roundR(), "")
            if foco and show_focused_index:
                token.fmt = ""
            output.add(extrap).addf(token.fmt, str(index).zfill(2)).add(token).add(extras).add(" ")
            i += 1

        size = 6
        if self.focused_index * size > frame.get_dx():
            output.cut_begin((self.focused_index + 1) * size - frame.get_dx())
        return output

    def draw_top_bar_content(self, frame):
        focused_unit_color = "B"
        value = self.get_focused_unit()
        info = Sentence()
        if self.wdir.get_solver().compile_error:
            info = Style.border_round("R", "Erro de compilação")
        elif value is not None and not self.is_all_right() and not self.mode == Mode.intro:
            info = value.str(pad = False)
            if self.locked_index:
                info = Style.border_round(focused_unit_color, info.get_text())
        frame.write(0, 0, Sentence().add(info).center(frame.get_dx()))

    def draw_top_bar(self):
        # construir mais uma solução
        _, cols = Fmt.get_size()
        frame = Frame(0, 0).set_size(3, cols)
        frame.set_header(self.build_top_line_header(frame))

        self.draw_top_bar_content(frame)
    
        frame.set_footer(self.build_top_bar_footer(frame), "")
        frame.draw()
        
    def two_column_mode(self):
        _, cols = Fmt.get_size()
        return cols < Sentence(" ").join(self.make_bottom_line()).len() + 2

    def make_bottom_line(self) -> List[Sentence]:
        cmds: List[Sentence] = []
        if Flags.others.is_true():
            cmds.append(Style.border_round("M", f"{DActions.rodar}[{DKeys.rodar}]"))
            # diff
            text = f"VER━╾h[{DKeys.diff}]" if self.settings.app.get_diff_mode() == "side" else f"v╼━HOR[{DKeys.diff}]"
            cmds.append(Style.border_round("M", text))
        
        cmds.append(Style.border_round("C", f"{DActions.sair}[{DKeys.sair}]"))
        if self.opener is not None:
            cmds.append(Style.border_round("C", f"{DActions.editar}[{DKeys.editar}]"))
        cmds.append(Style.border_round("G", f"{DActions.testar}[↲]"))
        
        color = "G" if Flags.others.is_true() else "Y"
        cmds.append(Style.border_sharp(color, f"{DActions.outros}[{DKeys.outros}]"))
        if Flags.others.is_true():
            # travar

            value = str(self.settings.app.get_timeout())
            if value == "0":
                value = "∞"
            cmds.append(
                Sentence()
                    .add(Style.roundL("M"))
                    .add(RToken("M", f"{DActions.tempo}"))
                    .add(RToken("M", "{}".format(value)))
                    .add(RToken("M", f"[{DKeys.tempo}]"))
                    .add(Style.roundR("M"))
            )
            travar = f"{DActions.fixar}[{DKeys.travar}]"
            color = "G" if self.locked_index else "M"
            cmds.append(Style.border_sharp(color, travar))


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
        if not self.mode == Mode.finished:
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
        elif self.param.is_up_down:
            line_list = Diff.mount_up_down_diff(unit, curses=True)
        else:
            line_list = Diff.mount_side_by_side_diff(unit, curses=True)

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

    def load_autoload_warning(self):
        if not self.wdir.is_autoload():
            return
        warning = Floating().set_header(" Seja bem vindo ").warning()
        warning.put_text("")
        warning.put_sentence(Sentence().addf("r", "Todos") + " os arquivos de código da pasta foram carregados automaticamente")
        warning.put_text("Sempre verifique no topo da tela quais arquivos foram carregados.")
        warning.put_text("Remova ou renomeie da pasta alvo os arquivo que não quer utilizar.")
        warning.put_text("")
        warning.put_text("Você também pode escolher quais arquivos deseja executar")
        warning.put_text("navegando até a pasta de destino e executando")
        warning.put_text("o comando 'tko run' com os arquivos desejados")
        warning.put_text("")
        warning.put_sentence(Sentence().addf("c", "tko run <arquivos> cases.tio")) 
        warning.put_text("")
        warning.put_sentence(Sentence().addf("r", "Exemplo: ").addf("c", "tko run main.c lib.c cases.tio")) 
        warning.put_text("")

        self.fman.add_input(warning)

    def get_solver_names(self):
        return sorted(self.wdir.solvers_names())
    
    def main(self, scr):
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global
        while not self.exit:
            if self.first_loop and self.first_run:
                self.first_loop = False
                self.load_autoload_warning()
            Fmt.clear()
            if self.mode == Mode.running:
                if self.wdir.get_solver().not_compiled():
                    self.draw_top_bar()
                    self.show_bottom_line()
                    self.show_compilling()
                    Fmt.refresh()
                    try:
                        self.wdir.get_solver().prepare_exec()
                    except CompileError as e:
                        self.fman.add_input(Floating("v>").error().put_text(e.message))
                        self.mode = Mode.finished
                    Fmt.clear()
                    self.draw_top_bar()
                    self.show_bottom_line()
                    Fmt.refresh()
                self.process_one()
            self.draw_top_bar()

            if self.mode == Mode.intro:
                self.print_centered_image(random_get(intro, self.get_folder()), "y")
            else:
                self.draw_main()
            
            self.show_bottom_line()

            if self.fman.has_floating():
                self.fman.draw_warnings()

            if self.mode == Mode.running:
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
        self.mode = Mode.running
        if self.wdir.is_autoload():
            self.wdir.autoload()
            self.wdir.get_solver().set_main(self.get_solver_names()[self.task.main_index])
        return lambda: Free.free_run(self.wdir.get_solver(), show_compilling=True, to_clear=True, wait_input=True)

    def run_test_mode(self):
        self.mode = Mode.running
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
        if self.mode == Mode.intro:
            self.mode = Mode.select
        if self.locked_index:
            self.fman.add_input(Floating("v>").warning().put_text("←\nAtividade travada\nAperte {} para destravar".format(DKeys.travar)))
            return
        if not self.wdir.get_solver().compile_error:
            self.focused_index = max(0, self.focused_index - 1)
            self.init = 1000

    def go_right(self):
        if self.mode == Mode.intro:
            self.mode = Mode.select
            self.focused_index = 0
            return
        if self.locked_index:
            self.fman.add_input(Floating("v>").warning().put_text("→\nAtividade travada\nAperte {} para destravar".format(DKeys.travar)))
            return
        if not self.wdir.get_solver().compile_error:
            self.focused_index = min(len(self.wdir.get_unit_list()) - 1, self.focused_index + 1)
            self.init = 1000

    def go_down(self):
        if self.mode == Mode.intro:
            self.mode = Mode.select
        self.init += 1

    def go_up(self):
        if self.mode == Mode.intro:
            self.mode = Mode.select
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
        if self.mode == Mode.intro:
            self.mode = Mode.select
        if self.locked_index:
            for i in range(len(self.results)):
                _, index = self.results[i]
                self.results[i] = (ExecutionResult.UNTESTED, index)
            self.fman.add_input(
                Floating("v>").warning()
                .put_text("Atividade travada")
                .put_sentence(Sentence("Aperte ").addf("g", DKeys.travar).add(" para destravar"))
                .put_sentence(Sentence("Use ").addf("g", "Enter").add(" para rodar os testes"))
            )

    def change_limit(self):
            valor = self.settings.app.get_timeout()
            if valor == 0:
                valor = 1
            else:
                valor *= 2
            if valor >= 5:
                valor = 0
            self.settings.app.set_timeout(valor)
            self.save_settings()
            nome = "∞" if valor == 0 else str(valor)
            self.fman.add_input(
                Floating("v>").warning()
                .put_text("Limite de tempo de execução alterado para")
                .put_text(f"{nome} segundos")
            )

    def process_key(self, key):
        key_esc = 27
        if key == ord('q') or key == key_esc or key == DKeys.backspace1:
            self.set_exit()
        elif key == curses.KEY_LEFT or key == ord(DKeys.left):
            self.go_left()
        elif key == curses.KEY_RIGHT or key == ord(DKeys.right):
            self.go_right()
        elif key == curses.KEY_DOWN or key == ord(DKeys.down):
            self.go_down()
        elif key == curses.KEY_UP or key == ord(DKeys.up):
            self.go_up()
        elif key == ord(DKeys.diff):
            self.param.is_up_down = not self.param.is_up_down
            self.save_settings()
            # self.init = 0
        elif key == ord(DKeys.principal):
            self.change_main()
        elif key == ord(DKeys.rodar):
            return self.run_exec_mode()
        elif key == ord(DKeys.testar):
            self.run_test_mode()
        elif key == ord(DKeys.travar):
            self.lock_unit()
        elif key == ord(DKeys.editar):
            if self.opener is not None:
                self.opener.open_code(open_dir=True)
        elif key == ord(DKeys.tempo):
            self.change_limit()
        elif key == ord(DKeys.outros):
            Flags.others.toggle()
        elif key == ord(DKeys.border):
            self.settings.app.toggle_nerdfonts()
        elif key != -1 and key != curses.KEY_RESIZE:
            self.send_char_not_found(key)

    def run(self):
        while True:
            free_run_fn = curses.wrapper(self.main)
            if free_run_fn == None:
                break
            else:
                while(free_run_fn()):
                    pass
