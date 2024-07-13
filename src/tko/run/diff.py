from typing import List, Optional, Tuple
import io

from ..util.term_color import  Color
from ..util.symbols import symbols
from ..util.ftext import FF, TK
from .basic import Unit, ExecutionResult
from .report import Report
from icecream import ic # type: ignore

class Diff:

    @staticmethod
    def make_line_arrow_up(a: str, b: str) -> FF:
        hdiff = FF()
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
    def render_white(text: FF, color: str = "") -> Optional[FF]:
        out = FF().add(text).replace(' ', TK(symbols.whitespace.text, color)).replace('\n', TK(symbols.newline.text, color))

        return out

    # create a string with both ta and tb side by side with a vertical bar in the middle
    @staticmethod
    def side_by_side(ta: List[FF], tb: List[FF], unequal: TK = symbols.unequal) -> List[FF]:
        cut = (Report.get_terminal_size() - 6) // 2
        upper = max(len(ta), len(tb))
        data: List[FF] = []

        for i in range(upper):
            a = ta[i] if i < len(ta) else FF("###############")
            b = tb[i] if i < len(tb) else FF("###############")
            if len(a) < cut:
                a = a.ljust(cut, TK(" "))
            # if len(a) > cut:
            #     a = a[:cut]
            if i >= len(ta) or i >= len(tb) or ta[i] != tb[i]:
                data.append(FF() + unequal + " " + a + " " + unequal + " " + b)
            else:
                data.append(FF() + symbols.vbar + " " + a + " " + symbols.vbar + " " + b)

        return data

    # a_text -> clean full received
    # b_text -> clean full expected
    # first_failure -> index of the first line unmatched 
    @staticmethod
    def first_failure_diff(a_text: str, b_text: str, first_failure: int) -> List[FF]:
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

        out_a, out_b = Diff.colorize_2_lines_diff(FF(first_a), FF(first_b))

        output: List[FF] = []

        output.append(FF().add(symbols.vbar).add(" ").add(out_a.ljust(greater)).addf("g", " (expected)"))
        output.append(FF().add(symbols.vbar).add(" ").add(out_b.ljust(greater)).addf("r", " (received)"))
        diff = Diff.make_line_arrow_up(first_a, first_b).ljust(greater)
        output.append(FF().add(symbols.vbar).add(" ").add(diff).addf("b", " (mismatch)"))
        return output

    @staticmethod
    def find_first_mismatch(line_a: FF, line_b: FF) -> int: 
        i = 0
        while i < len(line_a) and i < len(line_b):
            if line_a[i] != line_b[i]:
                return i
            i += 1
        return i
    
    @staticmethod
    def colorize_2_lines_diff(la: FF, lb: FF, neut: str = "", exp: str = "g", rec: str = "r") -> Tuple[FF, FF]:
        pos = Diff.find_first_mismatch(la, lb)
        lat = la.get_text()
        lbt = lb.get_text()
        a_out = FF().addf(neut, lat[0:pos]).addf(exp, lat[pos:])
        b_out = FF().addf(neut, lbt[0:pos]).addf(rec, lbt[pos:])
        return a_out, b_out

    # return a tuple of two strings with the diff and the index of the  first mismatch line
    @staticmethod
    def render_diff(a_text: str, b_text: str, pad: Optional[bool] = None) -> Tuple[List[FF], List[FF], int]:
        a_lines = a_text.splitlines()
        b_lines = b_text.splitlines()

        a_output: List[FF] = []
        b_output: List[FF] = []

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
            a_data = FF(get(a_lines, i))
            b_data = FF(get(b_lines, i))
            
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
    def mount_up_down_diff(unit: Unit, curses=False) -> List[FF]:
        output: List[FF] = []

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        if string_received is None:
            string_received = ""
        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received)
        string_input_list = [FF().add(symbols.vbar.text).add(" ").add(line) for line in string_input.split("\n")][:-1]
        unequal = symbols.unequal.text
        if unit.result == ExecutionResult.EXECUTION_ERROR:
            unequal = symbols.vbar
        expected_lines, received_lines = Diff.put_left_equal(expected_lines, received_lines, unequal)

        if not curses:
            output.append(Report.centralize("", symbols.hbar, "╭"))
            output.append(Report.centralize(unit.str(), " ", symbols.vbar))
            output.append(Report.centralize(FF().addf("b", " INPUT "), symbols.hbar, "├"))
        else:
            output.append(Report.centralize(FF().addf("b", " INPUT "), symbols.hbar, "╭"))

        output += string_input_list
            
        output.append(Report.centralize(FF().addf("g", " EXPECTED "), symbols.hbar, "├"))
        output += expected_lines
        # output.append("\n".join(expected_lines))
        rcolor = "r" if string_expected != string_received else "g"
        output.append(Report.centralize(FF().addf(rcolor, " RECEIVED "), symbols.hbar, "├"))
        output +=  received_lines

        if unit.result != ExecutionResult.EXECUTION_ERROR:
            output.append(Report.centralize(FF().addf("b", " WHITESPACE "),  symbols.hbar, "├"))
            output += Diff.first_failure_diff(string_expected, string_received, first_failure)
        output.append(Report.centralize("",  symbols.hbar, "╰"))

        return output

    @staticmethod
    def put_left_equal(exp_lines: List[FF], rec_lines: List[FF], unequal: str = symbols.unequal):

        max_size = max(len(exp_lines), len(rec_lines))

        for i in range(max_size):
            if i >= len(exp_lines) or i >= len(rec_lines) or (exp_lines[i] != rec_lines[i]):
                exp_lines[i] = FF() + unequal + " " + exp_lines[i]
                rec_lines[i] = FF() + unequal + " " + rec_lines[i]
            else:
                exp_lines[i] = FF() + symbols.vbar + " " + exp_lines[i]
                rec_lines[i] = FF() + symbols.vbar + " " + rec_lines[i]
        
        return exp_lines, rec_lines
            
    @staticmethod
    def title_side_by_side(left: FF, right: FF, filler: TK = TK(" "), middle: TK = TK(" "), prefix: TK = TK()) -> FF:
        half = int((Report.get_terminal_size() - len(middle)) / 2)
        line = FF()
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
            line = FF() + prefix + line
        return line

    @staticmethod
    def mount_side_by_side_diff(unit: Unit, curses=False) -> List[FF]:

        output: List[FF] = []

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
        input_headera = FF().addf("b", " INPUT ")
        input_headerb = FF().addf("b", " INPUT ")
        if not curses:
            output.append(Diff.title_side_by_side(input_headera, input_headerb, hbar, TK("┬"), TK("├")))
        else:
            output.append(Report.centralize(FF().addf("b", " INPUT "),  symbols.hbar, "╭"))
            # output.append(Diff.title_side_by_side(input_headera, input_headerb, hbar, TK("┬"), TK("╭")))

        if string_input != "":
            lines = [FF(x) for x in string_input.split("\n")[:-1]]
            output += Diff.side_by_side(lines, lines)
        expected_header = FF().addf("g", " EXPECTED ")
        rcolor = "r" if string_expected != string_received else "g"
        received_header = FF().addf(rcolor, " RECEIVED ")
        output.append(Diff.title_side_by_side(expected_header, received_header, hbar, TK("┼"), TK("├")))
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR:
            unequal = symbols.vbar
        output += Diff.side_by_side(expected_lines, received_lines, unequal)
        if unit.result != ExecutionResult.EXECUTION_ERROR:
            output.append(Report.centralize(FF().addf("b", " WHITESPACE "),  symbols.hbar, "├"))
            output += Diff.first_failure_diff(string_expected, string_received, first_failure)
        output.append(Report.centralize("",  symbols.hbar, "╰"))

        return output
