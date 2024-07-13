import curses
from .play.fmt import Fmt
from .run.basic import DiffMode, ExecutionResult, CompilerError, Param, Unit
from .execution import Execution
from .run.diff import Diff
from .util.ftext import FF, TK
from typing import List
from .play.frame import Frame
from .run.wdir import Wdir
from .run.report import Report
from .settings.settings_parser import SettingsParser
from .settings.geral_settings import GeralSettings
import os

class CDiff:

    def __init__(self, wdir: Wdir, param: Param.Basic):
        self.param = param
        self.results: List[TK] = []
        self.wdir = wdir
        self.exit = False
        self.index = 0

        self.init = 0   # index of first line to show
        self.length = 1  # length of diff
        self.space = 0  # dy space for draw

        self.finished = False
        self.resumes: List[str] = []
        self.first_error = -1

        self.sp = SettingsParser()
        self.settings = self.sp.load_settings()
        

    def save_settings(self):
        self.settings.geral.set(GeralSettings.diffdown, self.param.is_up_down)
        self.sp.save_settings()

    def set_exit(self):
        self.exit = True

    def end_processing(self):
        return len(self.results) == len(self.wdir.unit_list)

    def get_color(self, unit: Unit):
        if unit.result == ExecutionResult.SUCCESS:
            return "G"
        if unit.result == ExecutionResult.WRONG_OUTPUT:
            return "R"
        if unit.result == ExecutionResult.EXECUTION_ERROR:
            return "Y"
        return ""

    def sucesso(self):
        out1 = [
            "  _____ __ __     __    ___  _____ _____  ___  ",
            " / ___/|  |  |   /  ]  /  _]/ ___// ___/ /   \ ",
            "(   \_ |  |  |  /  /  /  [_(   \_(   \_ |     |",
            " \__  ||  |  | /  /  |    _]\__  |\__  ||  O  |",
            " /  \ ||  :  |/   \_ |   [_ /  \ |/  \ ||     |",
            " \    ||     |\     ||     |\    |\    ||     |",
            "  \___| \__,_| \____||_____| \___| \___| \___/ ",
        ]

        out2 = [
        "░▒▓███████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓████████▓▒░░▒▓███████▓▒░▒▓███████▓▒░░▒▓██████▓▒░  ",
        "░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░     ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░",
        "░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░     ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░",
        " ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓██████▓▒░  ░▒▓██████▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░",
        "       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░     ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░",
        "       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░     ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░",
        "░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓████████▓▒░▒▓███████▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░ "]

        out3 = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⢔⣶⣖⢂⢒⡐⠢⠤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⢊⠵⠒⣩⠟⠛⠙⠂⠀⠀⠉⠒⢤⣾⣖⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣀⡤⠄⣀⠀⠀⠀⠀⠀⢀⠔⡡⠊⠀⠀⠀⠁⣀⣀⠀⠀⠀⠀⠀⠀⠈⠉⠻⡆⠈⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢠⠋⠁⠀⠀⠈⠱⡄⠀⠀⡠⠃⡜⠀⠀⠀⠀⢀⣾⠗⠋⠛⢆⠀⠀⠀⣠⣤⣤⡄⠉⢢⠀⠑⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢼⠀⠀⠀⠀⠀⠀⠱⠀⢠⠃⢠⠃⠀⠀⠀⠀⢸⠋⣠⣤⡀⠘⡆⠀⢰⡿⠋⠉⠳⣄⠈⣆⠀⠐⡄⠀⠀⢀⠔⠂⠐⠲⢄⠀⠀⠀
⠀⠀⠀⠈⢆⠀⠀⠀⠀⠀⢀⢃⠆⠀⠀⠁⠀⠀⢄⣀⣹⠀⣷⣼⣿⠀⢻⠀⢿⣖⣹⣷⡀⠈⡆⠈⠀⠀⢰⡀⠰⠃⠀⠀⠀⠀⠀⡇⠀⠀
⠀⠀⠀⠀⠈⣆⠤⠤⠤⠤⠾⣼⡀⠀⠀⠀⠀⠀⢀⡀⠂⠙⠻⡓⠋⢀⡏⠀⠀⢿⢿⡽⠃⠀⡜⠀⠀⠀⠀⡇⡇⠀⠀⠀⠀⠀⡠⠁⠀⠀
⠀⠀⢀⠔⡩⠀⠀⠀⠀⠀⠀⠀⠉⠓⢄⠀⠀⠊⠁⠙⢕⠂⠀⠘⡖⠊⠀⠀⠀⠀⠑⡤⠔⠊⡉⠐⠀⠀⢀⣰⡼⠤⠤⠤⢄⣰⠁⠀⠀⠀
⠀⡰⠁⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡇⠀⠀⠀⠀⠈⣶⡤⣀⠀⠀⠀⠀⠀⠀⠀⠁⠠⣲⠖⠤⢠⠞⠉⠀⠀⠀⠀⠀⠀⠀⠁⠢⡀⠀
⢰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠉⠛⠒⢧⡀⠀⠀⠀⠀⠘⣷⣀⠉⠑⠒⠂⠒⢐⣦⠖⠋⠀⠀⠀⡗⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀
⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀⠀⠸⣿⣷⣦⣤⣤⣤⣾⠇⠀⠀⠀⠀⡴⠛⠉⠀⠀⠀⠀⠉⠐⠂⠀⠀⠀⠀⢠
⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠄⣀⡀⢀⠞⢄⠀⠀⠀⠀⠀⠘⢾⣿⣻⣿⣿⡟⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⠈⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⢎⠀⠈⠢⡀⠀⠀⠀⠀⠈⠛⠿⠿⢛⠁⠀⠀⠀⠀⠈⢆⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈
⠀⠈⢢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡜⠻⢤⡀⠈⠲⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠔⢻⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠉⠢⢄⡀⠀⠀⠀⠀⢀⡠⠔⠊⠀⠀⠀⠉⠓⠦⣀⣁⠀⠀⠀⠀⠀⢀⣀⠤⠒⠊⠀⠀⠈⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀
⠀⠀⠀⠀⠀⠀⠀⠉⢉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠒⠤⠤⠤⠤⠒⠊⠁⠀⠀⠀""".split("\n")

        out = out1
        lines, cols = Fmt.get_size()
        if cols > 70:
            out = out3
        if cols > 91:
            out = out2
        for i, line in enumerate(out):
            Fmt.write(i + 4, 1, FF().addf("g", line).center(cols - 2, TK(" ", " ")))


    def draw_scrollbar(self):
        if not self.has_any_error():
            return   
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

            # pre = int((self.init / self.length) * total)
            # pos = int((max(0, self.length - self.init - self.space) / self.length) * total)            
            # mid = total - pre - pos
            pre = int((self.init / self.length) * total)
            mid = int((self.space / self.length) * total)
            pos = (max(0, total - pre - mid))

            if _begin:
                pre -= 1
            if _end:
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

        elif self.length < self.space:
            bar.append(tr)
            for i in range(self.length - 2):
                bar.append(vbar)
            bar.append(br)

        lines, cols = Fmt.get_size()
        for i in range(len(bar)):
            Fmt.write(i + 3, cols - 1, FF().add(bar[i]))


    def draw_top_line(self):
        # construir mais uma solução
        if len(self.results) < len(self.wdir.unit_list):
            index = len(self.results)
            unit = self.wdir.unit_list[index]
            unit.result = Execution.run_unit(self.wdir.solver, unit)
            symbol = ExecutionResult.get_symbol(unit.result)
            color = self.get_color(unit)
            self.results.append(TK(symbol.text, color))
            if color != "G" and self.first_error == -1:
                self.first_error = len(self.results) - 1
                self.index = len(self.results) - 1


        lines, cols = Fmt.get_size()
        frame = Frame(0, 0).set_size(3, cols)
        pwd = os.getcwd()
        intro = self.wdir.resume()
        base = os.sep.join(pwd.split(os.sep)[:-1])
        last = pwd.split(os.sep)[-1]
        frame.set_header(FF().add(" ").add(base).add("/").addf("y", last).add("   ").add(intro).add(" ") , "<")
        unit = self.wdir.unit_list[self.index]
        frame.set_footer(FF().add(" ").add(unit.str(False)), "")
        frame.draw()

        x = 0
        i = 0
        for i, symbol in enumerate(self.results):
            foco = i == self.index
            extrap = "" if not foco else ">"
            extras = "" if not foco else "<"
            label = FF().add(extrap).addf(symbol.fmt, str(i).zfill(2)).add(symbol).add(extras)
            frame.write(0, x + 1 - len(extrap), label)
            x += 5
        
    def draw_bottom_line(self):
        cmds = (FF()
        .add(" ")
        .addf("/", "ReRun").add("[r]")
        .add(" ")
        .addf("/", "Move").add("[esq, dir]")
        .add(" ")
        .addf("/", "Scroll").add("[up, down]")
        .add(" ")
        .addf("/", "Diff").add("[d]")
        .add(" ")
        .addf("/", "Select").add("[0-9]")
        .add(" ")
        )
        lines, cols = Fmt.get_size()
        Fmt.write(lines - 1, 0, cmds.center(cols, TK(" ", "K")))

    def has_any_error(self):
        results = [unit.result for unit in self.wdir.unit_list]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return False
        return True          

    def draw_diff(self, unit: Unit):
        lines, cols = Fmt.get_size()
        self.space = lines - 4
        frame = Frame(2, -1).set_inner(self.space, cols - 1).set_border_square()
        # frame.draw()
        if not self.has_any_error():
            self.sucesso()
            return        
        Report.set_terminal_size(cols)
        if self.param.is_up_down:
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
            frame.write(i, 0, FF().add(line))
        return


    def main(self, scr):
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global
        while not self.exit:
            Fmt.erase()
            self.draw_top_line()
            unit = self.wdir.unit_list[self.index]
            self.draw_diff(unit)
            self.draw_scrollbar()
            self.draw_bottom_line()
            if not self.end_processing():
                Fmt.refresh()
            else:
                input = Fmt.getch()
                if input == ord('q'):
                    self.set_exit()
                elif input == curses.KEY_LEFT:
                    self.index = max(0, self.index - 1)
                    self.init = 0
                elif input == curses.KEY_RIGHT:
                    self.index = min(len(self.results) - 1, self.index + 1)
                    self.init = 0
                elif input == curses.KEY_DOWN:
                    self.init += 1
                elif input == curses.KEY_UP:
                    self.init = max(0, self.init - 1)
                elif input == ord('d'):
                    self.param.is_up_down = not self.param.is_up_down
                    self.save_settings()
                    self.init = 0
                elif input == ord('r'):
                    self.wdir.solver.prepare_exec()
                    self.results = []
                    self.first_error = -1
                elif input >= ord('0') and input <= ord('9'):
                    if input - ord('0') < len(self.results):
                        self.index = min(len(self.results) - 1, input - ord('0'))
                

    def run(self):
        curses.wrapper(self.main)
