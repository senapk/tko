from typing import List, Optional, Tuple
import io

from ..util.term_color import  Color
from ..util.symbols import symbols
from ..util.ftext import Sentence, Token
from .basic import Unit, ExecutionResult
from .report import Report

class Diff:

    @staticmethod
    def make_line_arrow_up(a: str, b: str) -> Sentence:
        hdiff = Sentence()
        first = True
        i = 0
        lim = max(len(a), len(b))
        while i < lim:
            if i >= len(a) or i >= len(b) or a[i] != b[i]:
                if first:
                    first = False
                    hdiff += symbols.arrow_up
                    return hdiff
            else:
                hdiff += " "
            i += 1
        return hdiff

    @staticmethod
    def render_white(text: Sentence, color: str = "") -> Optional[Sentence]:
        out = Sentence().add(text).replace(' ', Token(symbols.whitespace.text, color)).replace('\n', Token(symbols.newline.text, color))

        return out

    # create a string with both ta and tb side by side with a vertical bar in the middle
    @staticmethod
    def side_by_side(ta: List[Sentence], tb: List[Sentence], unequal: Token = symbols.unequal) -> List[Sentence]:
        cut = (Report.get_terminal_size() - 6) // 2
        upper = max(len(ta), len(tb))
        data: List[Sentence] = []

        for i in range(upper):
            a = ta[i] if i < len(ta) else Sentence("###############")
            b = tb[i] if i < len(tb) else Sentence("###############")
            if len(a) < cut:
                a = a.ljust(cut, Token(" "))
            # if len(a) > cut:
            #     a = a[:cut]
            if i >= len(ta) or i >= len(tb) or ta[i] != tb[i]:
                data.append(Sentence() + unequal + " " + a + " " + unequal + " " + b)
            else:
                data.append(Sentence() + symbols.vbar + " " + a + " " + symbols.vbar + " " + b)

        return data

    # a_text -> clean full received
    # b_text -> clean full expected
    # first_failure -> index of the first line unmatched 
    @staticmethod
    def first_failure_diff(a_text: str, b_text: str, first_failure: int) -> List[Sentence]:
        def get(vet, index):
            if index < len(vet):
                return Diff.render_white(vet[index])
            return ""

        a_render = a_text.splitlines(True)
        b_render = b_text.splitlines(True)

        first_a = get(a_render, first_failure)
        first_b = get(b_render, first_failure)
        greater = max(len(first_a), len(first_b))

        if first_failure > 0:
            lbefore = get(a_render, first_failure - 1)
            greater = max(greater, len(lbefore))

        out_a, out_b = Diff.colorize_2_lines_diff(Sentence(first_a), Sentence(first_b))

        output: List[Sentence] = []

        output.append(Sentence().add(symbols.vbar).add(" ").add(out_a.ljust(greater)).addf("g", " (expected)"))
        output.append(Sentence().add(symbols.vbar).add(" ").add(out_b.ljust(greater)).addf("r", " (received)"))
        diff = Diff.make_line_arrow_up(first_a, first_b).ljust(greater)
        output.append(Sentence().add(symbols.vbar).add(" ").add(diff).addf("b", " (mismatch)"))
        return output

    @staticmethod
    def find_first_mismatch(line_a: Sentence, line_b: Sentence) -> int: 
        i = 0
        while i < len(line_a) and i < len(line_b):
            if line_a[i] != line_b[i]:
                return i
            i += 1
        return i
    
    @staticmethod
    def colorize_2_lines_diff(la: Sentence, lb: Sentence, neut: str = "", exp: str = "g", rec: str = "r") -> Tuple[Sentence, Sentence]:
        pos = Diff.find_first_mismatch(la, lb)
        lat = la.get_text()
        lbt = lb.get_text()
        a_out = Sentence().addf(neut, lat[0:pos]).addf(exp, lat[pos:])
        b_out = Sentence().addf(neut, lbt[0:pos]).addf(rec, lbt[pos:])
        return a_out, b_out

    # return a tuple of two strings with the diff and the index of the  first mismatch line
    @staticmethod
    def render_diff(a_text: str, b_text: str, pad: Optional[bool] = None) -> Tuple[List[Sentence], List[Sentence], int]:
        a_lines = a_text.splitlines()
        b_lines = b_text.splitlines()

        a_output: List[Sentence] = []
        b_output: List[Sentence] = []

        a_size = len(a_lines)
        b_size = len(b_lines)
        
        first_failure = -1

        cut: int = 0
        if pad is True:
            cut = (Report.get_terminal_size() - 6) // 2

        max_size = max(a_size, b_size)

        # lambda function to return element in index i or empty if out of bounds
        def get(vet, index):
            out = ""
            if index < len(vet):
                out = vet[index]
            if pad is None:
                return out
            return out[:cut].ljust(cut)

        # get = lambda vet, i: vet[i] if i < len(vet) else ""

        for i in range(max_size):
            a_data = Sentence(get(a_lines, i))
            b_data = Sentence(get(b_lines, i))
            
            if i >= a_size or i >= b_size or a_lines[i] != b_lines[i]:
                if first_failure == -1:
                    first_failure = i
                a_out, b_out = Diff.colorize_2_lines_diff(a_data, b_data, "y")
                a_output.append(a_out)
                b_output.append(b_out)
            else:
                a_output.append(a_data)
                b_output.append(b_data)

        return a_output, b_output, first_failure

    @staticmethod
    def mount_up_down_diff(unit: Unit, curses=False) -> List[Sentence]:
        output: List[Sentence] = []

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        if string_received is None:
            string_received = ""
        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received)
        string_input_list = [Sentence().add(symbols.vbar.text).add(" ").add(line) for line in string_input.split("\n")][:-1]
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR or unit.result == ExecutionResult.COMPILATION_ERROR:
            unequal = symbols.vbar
        expected_lines, received_lines = Diff.put_left_equal(expected_lines, received_lines, unequal)

        if not curses:
            output.append(Report.centralize("", symbols.hbar, "╭"))
            output.append(Report.centralize(unit.str(), " ", symbols.vbar))
            output.append(Report.centralize(Sentence().addf("b", " INPUT "), symbols.hbar, "├"))
        else:
            output.append(Report.centralize(Sentence().addf("b", " INPUT "), symbols.hbar, "╭"))

        output += string_input_list
            
        output.append(Report.centralize(Sentence().addf("g", " EXPECTED "), symbols.hbar, "├"))
        output += expected_lines
        # output.append("\n".join(expected_lines))
        rcolor = "r" if string_expected != string_received else "g"
        output.append(Report.centralize(Sentence().addf(rcolor, " RECEIVED "), symbols.hbar, "├"))
        output +=  received_lines

        if unit.result != ExecutionResult.EXECUTION_ERROR and unit.result != ExecutionResult.COMPILATION_ERROR:
            output.append(Report.centralize(Sentence().addf("b", " WHITESPACE "),  symbols.hbar, "├"))
            output += Diff.first_failure_diff(string_expected, string_received, first_failure)
        output.append(Report.centralize("",  symbols.hbar, "╰"))

        return output

    @staticmethod
    def put_left_equal(exp_lines: List[Sentence], rec_lines: List[Sentence], unequal: Token = symbols.unequal):

        max_size = max(len(exp_lines), len(rec_lines))

        for i in range(max_size):
            if i >= len(exp_lines) or i >= len(rec_lines) or (exp_lines[i] != rec_lines[i]):
                exp_lines[i] = Sentence() + unequal + " " + exp_lines[i]
                rec_lines[i] = Sentence() + unequal + " " + rec_lines[i]
            else:
                exp_lines[i] = Sentence() + symbols.vbar + " " + exp_lines[i]
                rec_lines[i] = Sentence() + symbols.vbar + " " + rec_lines[i]
        
        return exp_lines, rec_lines
            
    @staticmethod
    def title_side_by_side(left: Sentence, right: Sentence, filler: Token = Token(" "), middle: Token = Token(" "), prefix: Token = Token()) -> Sentence:
        half = int((Report.get_terminal_size() - len(middle)) / 2)
        line = Sentence()
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
        if prefix != "":
            line.data[0].text = line.data[0].text[1:]
            line = Sentence() + prefix + line
        return line

    @staticmethod
    def mount_side_by_side_diff(unit: Unit, curses=False) -> List[Sentence]:

        output: List[Sentence] = []

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user
        if string_received is None:
            string_received = ""
        # dotted = "-"
        # vertical_separator = symbols.vbar
        hbar = symbols.hbar

        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received, True)
        if not curses:
            output.append(Report.centralize("", hbar, "╭"))
            output.append(Report.centralize(unit.str(), " ", "│"))
        input_headera = Sentence().addf("b", " INPUT ")
        input_headerb = Sentence().addf("b", " INPUT ")
        if not curses:
            output.append(Diff.title_side_by_side(input_headera, input_headerb, hbar, Token("┬"), Token("├")))
        else:
            output.append(Report.centralize(Sentence().addf("b", " INPUT "),  symbols.hbar, "╭"))
            # output.append(Diff.title_side_by_side(input_headera, input_headerb, hbar, TK("┬"), TK("╭")))

        if string_input != "":
            lines = [Sentence(x) for x in string_input.split("\n")[:-1]]
            output += Diff.side_by_side(lines, lines)
        expected_header = Sentence().addf("g", " EXPECTED ")
        rcolor = "r" if string_expected != string_received else "g"
        received_header = Sentence().addf(rcolor, " RECEIVED ")
        output.append(Diff.title_side_by_side(expected_header, received_header, hbar, Token("┼"), Token("├")))
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR or unit.result == ExecutionResult.COMPILATION_ERROR:
            unequal = symbols.vbar
        output += Diff.side_by_side(expected_lines, received_lines, unequal)
        if unit.result != ExecutionResult.EXECUTION_ERROR and unit.result != ExecutionResult.COMPILATION_ERROR:
            output.append(Report.centralize(Sentence().addf("b", " WHITESPACE "),  symbols.hbar, "├"))
            output += Diff.first_failure_diff(string_expected, string_received, first_failure)
        output.append(Report.centralize("",  symbols.hbar, "╰"))

        return output
