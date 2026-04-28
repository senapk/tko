from tko.run.diff_builder import DiffBuilder
from tko.run.unit import Unit
from tko.enums.execution_result import ExecutionResult
from tko.util.symbols import Symbols
from tko.util.rtext import RText

class DiffBuilderSide:
    def __init__(self, width: int, unit: Unit):
        self.width = width
        self.curses = False
        self.db = DiffBuilder(width)
        self.unit: Unit = unit
        self.output: list[RText] = []
        self.__to_insert_header = False
        self.__standalone_diff = False
        self.expected_received, self.first_failure = self.db.render_diff(self.unit.get_expected(), self.unit.get_received())

    def set_curses(self):
        self.curses = True
        return self

    def split_screen(self, a: RText | None, b: RText | None, unequal: RText | None = None) -> RText:
        if unequal is None:
            unequal = RText(Symbols.vbar)
        avaliable = self.width - 7 # 2 spaces before, 2 spaces after, 3 between
        cut = avaliable // 2
        if a is None or b is None or a != b:
            symb = unequal
        else:
            symb = RText(Symbols.vbar)
        ta = RText() + (a or RText())
        tb = RText() + (b or RText())
        ta = ta.ljust(cut, " ").trim_end(cut)
        tb = tb.ljust(cut, " ").trim_end(cut)
        line = symb + " " + ta + " " + symb + " " + tb + " "
        if self.width % 2 == 0:
            line += " "
        return line + Symbols.vbar

    def title_side_by_side(
        self,
        left: RText,
        right: RText,
        filler: RText | str = " ",
        middle: RText | str = " ",
        prefix: RText | str = "",
        posfix: RText | str = "",
    ) -> RText:
        if isinstance(filler, str):
            filler = RText(filler)
        if isinstance(middle, str):
            middle = RText(middle)
        if isinstance(prefix, str):
            prefix = RText(prefix)
        if isinstance(posfix, str):
            posfix = RText(posfix)
        avaliable = self.width - len(prefix) - len(posfix) - len(middle)
        half = avaliable // 2
        line = RText() + prefix

        a = left
        a = a.center(half, filler)
        if len(a) > half:
            a = a.trim_end(half)
        line += a
        line += middle
        b = right
        b = b.center(half, filler)
        if len(b) > half:
            b = b.trim_end(half)
        line += b
        if self.width % 2 == 0:
            line += filler
        line += posfix
        return line

    def to_insert_header(self, value: bool):
        self.__to_insert_header = value
        return self

    def standalone_diff(self):
        self.__standalone_diff = True
        return self

    def _insert_header(self):
        self.output.append(RText().fold_in(self.width, Symbols.hbar, "╭", "╮"))
        self.output.append(self.unit.str().fold_in(self.width, " ", "│", "│"))

    def _insert_input(self):
        # input header
        input_color = "b" if self.unit.get_expected() != self.unit.get_received() else "g"
        input_headera = RText(DiffBuilder.vinput, input_color)
        input_headerb = RText(DiffBuilder.vinput, input_color)
        if self.__to_insert_header:
            self.output.append(self.title_side_by_side(input_headera, input_headerb, Symbols.hbar, "┬", "├", "┤"))
        else:
            self.output.append(RText(DiffBuilder.vinput, input_color).fold_in(self.width, Symbols.hbar, "╭", "╮"))

        # input lines
        if self.unit.input != "":
            lines = [RText(x) for x in self.unit.input.splitlines()]
            for l in lines:
                self.output.append(self.split_screen(l, l))
    
    def _insert_expected_received(self):
        # expected and received header
        ecolor = "g" if self.unit.get_expected() == self.unit.get_received() else "y"
        expected_header = RText(DiffBuilder.vexpected, ecolor)
        rcolor = "r" if self.unit.get_expected() != self.unit.get_received() else "g"
        received_header = RText(DiffBuilder.vreceived, rcolor)
        if self.__standalone_diff:
            self.output.append(self.title_side_by_side(expected_header, received_header, Symbols.hbar, "┬", "╭", "╮"))
        else:
            self.output.append(self.title_side_by_side(expected_header, received_header, Symbols.hbar, "┼", "├", "┤"))
        # expected and received lines
        symbol = RText(Symbols.unequal)
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR:
            symbol = RText(Symbols.vbar)
        for exp, rec in self.expected_received:
            self.output.append(self.split_screen(exp, rec, symbol))

    def _insert_first_line_diff(self):
        if self.unit.get_expected() == self.unit.get_received() or self.unit.get_expected() == "":
            return
        self.output.append(RText(DiffBuilder.vunequal, "b").fold_in(self.width, Symbols.hbar, "├", "┤"))
        for line in self.db.first_failure_diff(self.unit.get_expected(), self.unit.get_received(), self.first_failure):
            width = self.width - 1
            self.output.append((RText("│") + line).ljust(width, " ") + "│")
        
    def _finish(self):
        if self.unit.get_expected() == self.unit.get_received() or self.unit.get_expected() == "":
            self.output.append(RText("┴").fold_in(self.width, Symbols.hbar, "╰", "╯"))
        else:
            self.output.append(RText().fold_in(self.width, Symbols.hbar, "╰", "╯"))

    def build_diff(self) -> list[RText]:
        self.output = []
        if self.__to_insert_header:
            self._insert_header()
        if not self.__standalone_diff:
            self._insert_input()
        self._insert_expected_received()
        self._insert_first_line_diff()
        self._finish()
        
        return self.output
