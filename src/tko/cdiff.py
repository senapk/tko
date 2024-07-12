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
import os

class CDiff:

    def __init__(self, wdir: Wdir, param: Param.Basic):
        self.param = param
        self.results: List[FF] = []
        self.wdir = wdir
        self.exit = False
        self.index = 0
        self.finished = False
        self.resumes: List[str] = []

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

    def draw_top_line(self):
        # construir mais uma solução
        if len(self.results) < len(self.wdir.unit_list):
            index = len(self.results)
            unit = self.wdir.unit_list[index]
            unit.result = Execution.run_unit(self.wdir.solver, unit)
            symbol = ExecutionResult.get_symbol(unit.result)
            color = self.get_color(unit)
            self.results.append(FF().addf(color, symbol.text))

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
            foco = "" if i != self.index else "B"
            extrap = "" if not foco else ">"
            extras = "" if not foco else "<"
            label = FF().add(extrap).addf(foco + "/kW", str(i).zfill(2)).add(symbol).add(extras)
            frame.write(0, x + 1 - len(extrap), label)
            x += 5
        
    def draw_bottom_line(self):
        cmds = (FF()
        .add(" ")
        .addf("/", "Move").add("[esq, dir]")
        .add(" ")
        .addf("/", "Diff").add("[d]")
        .add(" ")
        .addf("/", "Select").add("[0-9]")
        .add(" ")
        )
        lines, cols = Fmt.get_size()
        Fmt.write(lines - 1, 0, cmds.center(cols, TK(" ")))

    def draw_diff(self, unit: Unit):
        lines, cols = Fmt.get_size()
        frame = Frame(2, -1).set_size(lines - 2, cols + 1).set_border_square()
        # frame.draw()
        results = [unit.result for unit in self.wdir.unit_list]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return        
        Report.set_terminal_size(cols)
        if self.param.is_up_down:
            lines = Diff.mount_up_down_diff(unit, curses=True)
        else:
            lines = Diff.mount_side_by_side_diff(unit, curses=True)

        for i, line in enumerate(lines):
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
            self.draw_bottom_line()
            if not self.end_processing():
                Fmt.refresh()
            else:
                input = Fmt.getch()
                if input == ord('q'):
                    self.set_exit()
                elif input == curses.KEY_LEFT:
                    self.index = max(0, self.index - 1)
                elif input == curses.KEY_RIGHT:
                    self.index = min(len(self.results) - 1, self.index + 1)
                elif input == ord('d'):
                    self.param.is_up_down = not self.param.is_up_down
                elif input >= ord('0') and input <= ord('9'):
                    if input - ord('0') < len(self.results):
                        self.index = min(len(self.results) - 1, input - ord('0'))

    def run(self):
        curses.wrapper(self.main)