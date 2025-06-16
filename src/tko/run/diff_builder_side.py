from tko.run.diff_builder import DiffBuilder
from tko.run.unit import Unit
from tko.enums.execution_result import ExecutionResult
from tko.util.symbols import symbols
from tko.util.text import Text

class DiffBuilderSide:
    def __init__(self, width: int, unit: Unit):
        self.width = width
        self.curses = False
        self.db = DiffBuilder(width)
        self.unit: Unit = unit
        self.output: list[Text] = []
        self.__to_insert_header = False
        self.__standalone_diff = False
        self.expected_received, self.first_failure = self.db.render_diff(self.unit.get_expected(), self.unit.get_received())

    def set_curses(self):
        self.curses = True
        return self

    def split_screen(self, a: Text | None, b: Text | None, unequal: Text.Token = symbols.vbar) -> Text:
        avaliable = self.width - 7 # 2 spaces before, 2 spaces after, 3 between
        cut = avaliable // 2
        if a is None or b is None or a != b:
            symb = unequal
        else:
            symb = symbols.vbar
        ta = Text() + a
        tb = Text() + b
        ta = ta.ljust(cut, Text.Token(" ")).trim_end(cut)
        tb = tb.ljust(cut, Text.Token(" ")).trim_end(cut)
        line = symb + " " + ta + " " + symb + " " + tb + " "
        if self.width % 2 == 0:
            line += " "
        return line + symbols.vbar

    def title_side_by_side(self, left: Text, right: Text, filler: Text.Token = Text.Token(" "), middle: Text.Token = Text.Token(" "), prefix: Text.Token = Text.Token(), posfix: Text.Token = Text.Token()) -> Text:
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

    def standalone_diff(self):
        self.__standalone_diff = True
        return self

    def _insert_header(self):
        self.output.append(Text().fold_in(self.width, symbols.hbar, "╭", "╮"))
        self.output.append(self.unit.str().fold_in(self.width, " ", "│", "│"))

    def _insert_input(self):
        # input header
        input_color = "b" if self.unit.get_expected() != self.unit.get_received() else "g"
        input_headera = Text().addf(input_color, DiffBuilder.vinput)
        input_headerb = Text().addf(input_color, DiffBuilder.vinput)
        if self.__to_insert_header:
            self.output.append(self.title_side_by_side(input_headera, input_headerb, symbols.hbar, Text.Token("┬"), Text.Token("├"), Text.Token("┤")))
        else:
            self.output.append(Text().addf(input_color, DiffBuilder.vinput).fold_in(self.width, symbols.hbar, "╭", "╮"))

        # input lines
        if self.unit.inserted != "":
            lines = [Text().add(x) for x in self.unit.inserted.splitlines()]
            for l in lines:
                self.output.append(self.split_screen(l, l))
    
    def _insert_expected_received(self):
        # expected and received header
        ecolor = "g" if self.unit.get_expected() == self.unit.get_received() else "y"
        expected_header = Text().addf(ecolor, DiffBuilder.vexpected)
        rcolor = "r" if self.unit.get_expected() != self.unit.get_received() else "g"
        received_header = Text().addf(rcolor, DiffBuilder.vreceived)
        if self.__standalone_diff:
            self.output.append(self.title_side_by_side(expected_header, received_header, symbols.hbar, Text.Token("┬"), Text.Token("╭"), Text.Token("╮")))
        else:
            self.output.append(self.title_side_by_side(expected_header, received_header, symbols.hbar, Text.Token("┼"), Text.Token("├"), Text.Token("┤")))
        # expected and received lines
        symbol = symbols.unequal
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR:
            symbol = symbols.vbar
        for exp, rec in self.expected_received:
            self.output.append(self.split_screen(exp, rec, symbol))

    def _insert_first_line_diff(self):
        if self.unit.get_expected() == self.unit.get_received() or self.unit.get_expected() == "":
            return
        self.output.append(Text().addf("b", DiffBuilder.vunequal).fold_in(self.width, symbols.hbar, "├", "┤"))
        for line in self.db.first_failure_diff(self.unit.get_expected(), self.unit.get_received(), self.first_failure):
            width = self.width - 1
            self.output.append(Text().add("│").add(line).ljust(width, Text.Token(" ")).add("│"))
        
    def _finish(self):
        if self.unit.get_expected() == self.unit.get_received() or self.unit.get_expected() == "":
            self.output.append(Text().add("┴").fold_in(self.width, symbols.hbar, "╰", "╯"))
        else:
            self.output.append(Text().fold_in(self.width, symbols.hbar, "╰", "╯"))

    def build_diff(self) -> list[Text]:
        self.output = []
        if self.__to_insert_header:
            self._insert_header()
        if not self.__standalone_diff:
            self._insert_input()
        self._insert_expected_received()
        self._insert_first_line_diff()
        self._finish()
        
        return self.output