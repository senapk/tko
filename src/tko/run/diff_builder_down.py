from tko.run.diff_builder import DiffBuilder
from tko.run.unit import Unit
from tko.enums.execution_result import ExecutionResult
from tko.util.symbols import Symbols
from tko.util.rtext import RText


class DiffBuilderDown:
    def __init__(self, width: int, unit: Unit):
        self.width = width
        self.curses = False
        self.db = DiffBuilder(width)
        self.unit = unit
        self.output: list[RText] = []
        self.__to_insert_header = False
        self.__standalone_diff = False
        self.no_diff_mode = self.unit.input == "" and self.unit.get_expected() == ""
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
    def put_left_equal(exp_rec_list: list[tuple[RText | None, RText | None]], unequal: RText | None) -> list[tuple[RText, RText]]:
        if unequal is None:
            unequal = RText(Symbols.unequal)

        output: list[tuple[RText, RText]] = []
        for exp, rec in exp_rec_list:
            if exp is None or rec is None or exp != rec:
                exp_lines = RText() + unequal + " " + (exp or RText())
                rec_lines = RText() + unequal + " " + (rec or RText())
            else:
                exp_lines = RText(Symbols.vbar) + " " + exp
                rec_lines = RText(Symbols.vbar) + " " + rec
            output.append((exp_lines, rec_lines))
        return output

    def insert_header(self):
        self.output.append(RText().fold_in(self.width, Symbols.hbar, "╭", "╮"))
        self.output.append(self.unit.str().fold_in(self.width, " ", Symbols.vbar, Symbols.vbar))

    def insert_input(self):
        color = "g" if self.unit.get_expected() == self.unit.get_received() else "b"
        # header
        if self.__to_insert_header:
            self.output.append(RText(DiffBuilder.vinput, color).fold_in(self.width, Symbols.hbar, "├", "┤"))
        else:
            self.output.append(RText(DiffBuilder.vinput, color).fold_in(self.width, Symbols.hbar, "╭", "╮"))
        # lines
        for line in self.unit.input.splitlines():
            self.output.append((RText(Symbols.vbar) + " " + line).ljust(self.width - 1, " ") + Symbols.vbar)

    def insert_expected(self):
        if self.no_diff_mode:
            return
        if self.unit.get_expected() == "":
            return
        color = "g" if self.unit.get_expected() == self.unit.get_received() else "y"
        if self.__standalone_diff:
            opening = "╭"
            ending = "╮"
        else:
            opening = "├"
            ending = "┤" if self.curses else "╯"
        self.output.append(RText(DiffBuilder.vexpected, color).fold_in(self.width, Symbols.hbar, opening, ending))
        for line, _ in self.expected_received:
            if line is not None:
                if self.curses:
                    self.output.append(line.ljust(self.width - 1, " ") + Symbols.vbar)
                else:
                    self.output.append(line)

    def insert_received(self):
        # headers
        color = "g" if self.unit.get_expected() == self.unit.get_received() else "r"
        if self.no_diff_mode:
            color = "g"
            opening = "╭"
            ending = "╮"
        else:
            opening = "├"
            ending = "┤" if self.curses else Symbols.hbar
        self.output.append(RText(DiffBuilder.vreceived, color).fold_in(self.width, Symbols.hbar, opening, ending))

        # lines
        received: list[RText] = []
        for _, line in self.expected_received:
            if line is not None:
                received.append(line)
        while len(received) > 1 and len(received[-1]) == 2:
            received.pop()
        
        for line in received:
                if self.curses:
                    self.output.append(line.ljust(self.width - 1, " ").trim_end(self.width) + Symbols.vbar)
                else:
                    self.output.append(line)


    def insert_mismatch(self) -> bool:
        include_rendering = False
        if self.unit.get_expected() != self.unit.get_received() and self.unit.get_expected() != "":
            include_rendering = True
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR:
            include_rendering = False

        if not include_rendering:
            return False
        ending = "┤" if self.curses else "╮"
        self.output.append(RText(DiffBuilder.vunequal, "b").fold_in(self.width, Symbols.hbar, "├", ending))
        for line in self.db.first_failure_diff(self.unit.get_expected(), self.unit.get_received(), self.first_failure):
            self.output.append((RText("│") + line).ljust(self.width - 1, " ") + "│")
        return True

    def end_frame(self, mistatch_inserted: bool):
        end = "╯" if mistatch_inserted else Symbols.hbar
        self.output.append(RText().fold_in(self.width, Symbols.hbar, "╰", end))

    def build_diff(self) -> list[RText]:
        if self.__to_insert_header:
            self.insert_header()
        if not self.no_diff_mode and not self.__standalone_diff:
            self.insert_input()
        symb = RText(Symbols.unequal)
        if self.unit.result == ExecutionResult.EXECUTION_ERROR or self.unit.result == ExecutionResult.COMPILATION_ERROR or self.unit.get_expected() == "":
            symb = RText(Symbols.vbar)
        left_equal = self.put_left_equal(self.expected_received, symb)

        self.expected_received.clear()
        for exp, rec in left_equal:
            self.expected_received.append((exp, rec))

        self.insert_expected()
        self.insert_received()
        mistatch_inserted = self.insert_mismatch()
        self.end_frame(mistatch_inserted)

        return self.output
