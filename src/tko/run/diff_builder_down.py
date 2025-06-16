from tko.run.diff_builder import DiffBuilder
from tko.run.unit import Unit
from tko.enums.execution_result import ExecutionResult
from tko.util.symbols import symbols
from tko.util.text import Text


class DiffBuilderDown:
    def __init__(self, width: int, unit: Unit):
        self.width = width
        self.curses = False
        self.db = DiffBuilder(width)
        self.unit = unit
        self.output: list[Text] = []
        self.__to_insert_header = False
        self.__standalone_diff = False
        self.no_diff_mode = self.unit.inserted == "" and self.unit.get_expected() == ""
        self.expected_received, self.first_failure = self.db.render_diff(self.unit.get_expected(), self.unit.get_received())

    def to_insert_header(self):
        self.__to_insert_header = True
        return self
    
    def standalone_diff(self):
        self.__standalone_diff = True
        return self

    def set_curses(self):
        self.curses = True
        return self

    @staticmethod
    def put_left_equal(exp_rec_list: list[tuple[Text | None, Text | None]], unequal: Text.Token = symbols.unequal) -> list[tuple[Text, Text]]:

        output: list[tuple[Text, Text]] = []
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
        self.output.append(Text().fold_in(self.width, symbols.hbar, "╭", "╮"))
        self.output.append(self.unit.str().fold_in(self.width, " ", symbols.vbar, symbols.vbar))

    def insert_input(self):
        color = "g" if self.unit.get_expected() == self.unit.get_received() else "b"
        # header
        if self.__to_insert_header:
            self.output.append(Text().addf(color, DiffBuilder.vinput).fold_in(self.width, symbols.hbar, "├", "┤"))
        else:
            self.output.append(Text().addf(color, DiffBuilder.vinput).fold_in(self.width, symbols.hbar, "╭", "╮"))
        # lines
        for line in self.unit.inserted.splitlines():
            self.output.append(Text().add(symbols.vbar).add(" ").add(line).ljust(self.width - 1, Text.Token(" ")).add(symbols.vbar))

    def insert_expected(self):
        if self.no_diff_mode:
            return
        if self.unit.get_expected() == "":
            return
        color = "g" if self.unit.get_expected() == self.unit.get_received() else "y"
        if self.__standalone_diff:
            self.output.append(Text().addf(color, DiffBuilder.vexpected).fold_in(self.width, symbols.hbar, "╭", "╮"))
        else:
            self.output.append(Text().addf(color, DiffBuilder.vexpected).fold_in(self.width, symbols.hbar, "├", "┤"))
        for line, _ in self.expected_received:
            if line is not None:
                self.output.append(line.ljust(self.width - 1, Text.Token(" ")).add(symbols.vbar))

    def insert_received(self):
        # headers
        color = "g" if self.unit.get_expected() == self.unit.get_received() else "r"
        if self.no_diff_mode:
            color = "g"
            self.output.append(Text().addf(color, DiffBuilder.vreceived).fold_in(self.width, symbols.hbar, "╭", "╮"))
        else:
            self.output.append(Text().addf(color, DiffBuilder.vreceived).fold_in(self.width, symbols.hbar, "├", "┤"))

        # lines
        for _, line in self.expected_received:
            if line is not None:
                self.output.append(line.ljust(self.width - 1, Text.Token(" ")).trim_end(self.width).add(symbols.vbar))

    def insert_first_line_diff(self):
        include_rendering = False
        if self.unit.get_expected() != self.unit.get_received() and self.unit.get_expected() != "":
            include_rendering = True
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR:
            include_rendering = False

        if not include_rendering:
            return
        self.output.append(Text().addf("b", DiffBuilder.vunequal).fold_in(self.width, symbols.hbar, "├", "┤"))
        for line in self.db.first_failure_diff(self.unit.get_expected(), self.unit.get_received(), self.first_failure):
            self.output.append(Text().add("│").add(line).ljust(self.width - 1, Text.Token(" ")).add("│"))

    def end_frame(self):
        self.output.append(Text().fold_in(self.width, symbols.hbar, "╰", "╯"))

    def build_diff(self) -> list[Text]:
        if self.__to_insert_header:
            self.insert_header()
        if not self.no_diff_mode and not self.__standalone_diff:
            self.insert_input()
        symb = symbols.unequal
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR or self.unit.get_expected() == "":
            symb = symbols.vbar
        left_equal = self.put_left_equal(self.expected_received, symb)

        self.expected_received.clear()
        for exp, rec in left_equal:
            self.expected_received.append((exp, rec))

        self.insert_expected()
        self.insert_received()
        self.insert_first_line_diff()
        self.end_frame()

        return self.output