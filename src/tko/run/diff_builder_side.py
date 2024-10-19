from tko.run.diff_builder import DiffBuilder
from tko.run.unit import Unit
from tko.util.consts import ExecutionResult
from tko.util.symbols import symbols
from tko.util.text import Text, Token


from typing import List


class SideDiff:
    def __init__(self, width: int, unit: Unit):
        self.width = width
        self.curses = False
        self.db = DiffBuilder(width)
        self.unit: Unit = unit
        self.output: List[Text] = []
        self.__to_insert_header = False
        self.expected_received, self.first_failure = self.db.render_diff(self.unit.expected, self.unit.received)

    def set_curses(self):
        self.curses = True
        return self

    def split_screen(self, a: Text | None, b: Text | None, unequal: Token = symbols.vbar) -> Text:
        avaliable = self.width - 7 # 2 spaces before, 2 spaces after, 3 between
        cut = avaliable // 2
        if a is None or b is None or a != b:
            symb = unequal
        else:
            symb = symbols.vbar
        ta = Text() + a
        tb = Text() + b
        ta = ta.ljust(cut, Token(" ")).trim_end(cut)
        tb = tb.ljust(cut, Token(" ")).trim_end(cut)
        line = symb + " " + ta + " " + symb + " " + tb + " "
        if self.width % 2 == 0:
            line += " "
        return line + symbols.vbar

    def title_side_by_side(self, left: Text, right: Text, filler: Token = Token(" "), middle: Token = Token(" "), prefix: Token = Token(), posfix: Token = Token()) -> Text:
        avaliable = self.width - len(prefix) - len(posfix) - len(middle)
        half = avaliable // 2
        line = Text() + prefix

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

    def _insert_header(self):
        self.output.append(Text("").fold_in(self.width, symbols.hbar, "╭", "╮"))
        self.output.append(self.unit.str().fold_in(self.width, " ", "│", "│"))

    def _insert_input(self):
        # input header
        input_color = "b" if self.unit.expected != self.unit.received else "g"
        input_headera = Text().addf(input_color, DiffBuilder.vinput)
        input_headerb = Text().addf(input_color, DiffBuilder.vinput)
        if self.__to_insert_header:
            self.output.append(self.title_side_by_side(input_headera, input_headerb, symbols.hbar, Token("┬"), Token("├"), Token("┤")))
        else:
            self.output.append(Text().addf(input_color, DiffBuilder.vinput).fold_in(self.width, symbols.hbar, "╭", "╮"))

        # input lines
        if self.unit.input != "":
            lines = [Text(x) for x in self.unit.input.split("\n")[:-1]]
            for l in lines:
                self.output.append(self.split_screen(l, l))
    
    def _insert_expected_received(self):
        # expected and received header
        expected_header = Text().addf("g", DiffBuilder.vexpected)
        rcolor = "r" if self.unit.expected != self.unit.received else "g"
        received_header = Text().addf(rcolor, DiffBuilder.vreceived)
        self.output.append(self.title_side_by_side(expected_header, received_header, symbols.hbar, Token("┼"), Token("├"), Token("┤")))
        # expected and received lines
        symbol = symbols.unequal
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR:
            symbol = symbols.vbar
        for exp, rec in self.expected_received:
            self.output.append(self.split_screen(exp, rec, symbol))

    def _insert_first_line_diff(self):
        self.output.append(Text().addf("b", DiffBuilder.vunequal).fold_in(self.width, symbols.hbar, "├", "┤"))
        for line in self.db.first_failure_diff(self.unit.expected, self.unit.received, self.first_failure):
            width = self.width - 1
            self.output.append(Text("│").add(line).ljust(width, Token(" ")).add("│"))
        
    def _finish(self):
        self.output.append(Text("").fold_in(self.width, symbols.hbar, "╰", "╯"))

    def build_diff(self) -> List[Text]:
        self.output = []
        if self.__to_insert_header:
            self._insert_header()
        self._insert_input()
        self._insert_expected_received()
        self._insert_first_line_diff()
        self._finish()
        
        return self.output