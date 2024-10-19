from tko.run.diff_builder import DiffBuilder
from tko.run.unit import Unit
from tko.util.consts import ExecutionResult
from tko.util.symbols import symbols
from tko.util.text import Text, Token


from typing import List, Tuple


class DownDiff:
    def __init__(self, width: int, unit: Unit):
        self.width = width
        self.curses = False
        self.db = DiffBuilder(width)
        self.unit = unit
        self.output: List[Text] = []
        self.__to_insert_header = False
        self.no_diff_mode = self.unit.input == "" and self.unit.expected == ""
        self.expected_received, self.first_failure = self.db.render_diff(self.unit.expected, self.unit.received)

    def to_insert_header(self):
        self.__to_insert_header = True
        return self

    def set_curses(self):
        self.curses = True
        return self

    @staticmethod
    def put_left_equal(exp_rec_list: List[Tuple[Text | None, Text | None]], unequal: Token = symbols.unequal):

        output: List[Tuple[Text, Text]] = []
        for exp, rec in exp_rec_list:
            if exp is None or rec is None or exp != rec:
                exp_lines = Text() + unequal + " " + exp
                rec_lines = Text() + unequal + " " + rec
            else:
                exp_lines = Text() + symbols.vbar + " " + exp
                rec_lines = Text() + symbols.vbar + " " + rec
            output.append((exp_lines, rec_lines))
        return output

    def insert_header(self):
        self.output.append(Text("").fold_in(self.width, symbols.hbar, "╭", "╮"))
        self.output.append(self.unit.str().fold_in(self.width, " ", symbols.vbar, symbols.vbar))

    def insert_input(self):
        color = "g" if self.unit.expected == self.unit.received else "b"
        # header
        if self.__to_insert_header:
            self.output.append(Text().addf(color, DiffBuilder.vinput).fold_in(self.width, symbols.hbar, "├", "┤"))
        else:
            self.output.append(Text().addf(color, DiffBuilder.vinput).fold_in(self.width, symbols.hbar, "╭", "╮"))
        # lines
        for line in self.unit.input.split("\n")[:-1]:
            self.output.append(Text().add(symbols.vbar).add(" ").add(line).ljust(self.width - 1, Token(" ")).add(symbols.vbar))

    def insert_expected(self):
        if self.no_diff_mode:
            return
        # color = "g" if self.unit.expected == self.unit.received else "b"
        # self.output.append(Text().addf(color, DiffBuilder.vreceived).fold_in(self.width, symbols.hbar, "╭", "╮"))
        if self.unit.expected == "":
            return
        self.output.append(Text().addf("g", DiffBuilder.vexpected).fold_in(self.width, symbols.hbar, "├", "┤"))
        for line, _ in self.expected_received:
            if line is not None:
                self.output.append(line.ljust(self.width - 1, Token(" ")).add(symbols.vbar))

    def insert_received(self):
        # headers
        color = "r" if self.unit.expected == self.unit.received else "g"
        if self.no_diff_mode:
            color = "g"
            self.output.append(Text().addf(color, DiffBuilder.vreceived).fold_in(self.width, symbols.hbar, "╭", "╮"))
        else:
            self.output.append(Text().addf(color, DiffBuilder.vreceived).fold_in(self.width, symbols.hbar, "├", "┤"))

        # lines
        for _, line in self.expected_received:
            if line is not None:
                self.output.append(line.ljust(self.width - 1, Token(" ")).trim_end(self.width).add(symbols.vbar))

    def insert_first_line_diff(self):
        include_rendering = False
        if self.unit.expected != self.unit.received and self.unit.expected != "":
            include_rendering = True
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR:
            include_rendering = False

        if not include_rendering:
            return
        self.output.append(Text().addf("b", DiffBuilder.vunequal).fold_in(self.width, symbols.hbar, "├", "┤"))
        for line in self.db.first_failure_diff(self.unit.expected, self.unit.received, self.first_failure):
            self.output.append(Text("│").add(line).ljust(self.width - 1, Token(" ")).add("│"))

    def end_frame(self):
        self.output.append(Text("").fold_in(self.width, symbols.hbar, "╰", "╯"))

    def build_diff(self) -> List[Text]:
        if self.__to_insert_header:
            self.insert_header()
        if not self.no_diff_mode:
            self.insert_input()
        symb = symbols.unequal
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR or self.unit.expected == "":
            symb = symbols.vbar
        self.expected_received = self.put_left_equal(self.expected_received, symb)
        self.insert_expected()
        self.insert_received()
        self.insert_first_line_diff()
        self.end_frame()

        return self.output