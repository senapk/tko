import curses
from .play.fmt import Fmt
from .run.basic import DiffMode, ExecutionResult, CompilerError, Param, Unit
from .execution import Execution
from .run.diff import Diff
from .util.ftext import Ftext
from typing import List
from .util.term_color import Color
from .play.frame import Frame
from .run.wdir import Wdir
import os

class CDiff:

    def __init__(self, wdir: Wdir, param: Param.Basic):
        self.param = param
        self.results: List[Ftext] = []
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
        lines, cols = Fmt.get_size()
        frame = Frame(0, 0).set_size(3, cols)

        pwd = os.getcwd()
        frame.set_header(Ftext().add(f" {pwd} ") , "<")
        intro = Color.remove_colors(self.wdir.resume())
        if intro.startswith("=>"):
            intro = intro[2:]
        intro += " "
        frame.set_footer(Ftext().add(intro))
        frame.draw()

        
        # construir mais uma solução
        if len(self.results) < len(self.wdir.unit_list):
            index = len(self.results)
            unit = self.wdir.unit_list[index]
            unit.result = Execution.run_unit(self.wdir.solver, unit)
            symbol = Color.remove_colors(ExecutionResult.get_symbol(unit.result))
            color = self.get_color(unit)
            self.results.append(Ftext().addf(color, symbol))

        x = 0
        i = 0
        for i, symbol in enumerate(self.results):
            foco = "" if i != self.index else "B"
            label = Ftext().addf(foco + "/kW", str(i).zfill(2)).add(symbol)
            frame.write(0, x, label)
            x += 5
        
        if self.end_processing() and not self.finished:
            self.resumes = Color.remove_colors(self.wdir.unit_list_resume()).split("\n")
            self.finished = True

    def draw_bottom_line(self):
        cmds = (Ftext()
        .add(" ")
        .addf("/", "Move").add("[esq, dir]")
        .add(" ")
        .addf("/", "Diff").add("[d]")
        .add(" ")
        .addf("/", "Select").add("[0-9]")
        .add(" ")
        )

    def draw_diff(self):
        lines, cols = Fmt.get_size()
        frame = Frame(2, -1).set_size(lines - 4, cols + 1).set_border_none()
        results = [unit.result for unit in self.wdir.unit_list]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return
        # lines, cols = Fmt.get_size()
        # frame = Frame(3, -1).set_size(lines - 3, cols)
        # frame.set_header(Sentence().add(self.resumes[self.index]))
        # frame.draw()
        
        unit = self.wdir.unit_list[self.index]
        if self.param.is_up_down:
            value = Diff.mount_up_down_diff(unit)
        else:
            value = Diff.mount_side_by_side_diff(unit)

        for i, line in enumerate(value.split("\n")):
            frame.write(i, 0, Ftext().add(Color.remove_colors(line)))
        return


    def main(self, scr):
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global
        while not self.exit:
            Fmt.erase()
            self.draw_top_line()
            self.draw_diff()
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