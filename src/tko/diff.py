from typing import List, Optional, Tuple
import io

from .format import Colored, Color, Report, symbols
from .basic import Unit
from .basic import ExecutionResult


class Diff:

    @staticmethod
    def make_line_arrow_up(a: str, b: str) -> str:
        hdiff = ""
        first = True
        i = 0
        lim = max(len(a), len(b))
        while i < lim:
            if i >= len(a) or i >= len(b) or a[i] != b[i]:
                if first:
                    first = False
                    hdiff += symbols.arrow_up;
            else:
                hdiff += " "
            i += 1
        return hdiff

    @staticmethod
    def render_white(text: Optional[str], color: Optional[Color] = None) -> Optional[str]:
        if text is None:
            return None
        if color is None:
            text = text.replace(' ', symbols.whitespace)
            text = text.replace('\n', symbols.newline + '\n')
            return text
        text = text.replace(' ', Colored.paint(symbols.whitespace, color))
        text = text.replace('\n', Colored.paint(symbols.newline, color) + '\n')
        return text

    # create a string with both ta and tb side by side with a vertical bar in the middle
    @staticmethod
    def side_by_side(ta: List[str], tb: List[str], unequal: str = symbols.unequal):
        cut = (Report.get_terminal_size() - 6) // 2
        upper = max(len(ta), len(tb))
        data = []

        for i in range(upper):
            a = ta[i] if i < len(ta) else "###############"
            b = tb[i] if i < len(tb) else "###############"
            if len(a) < cut:
                a = a.ljust(cut)
            # if len(a) > cut:
            #     a = a[:cut]
            if i >= len(ta) or i >= len(tb) or ta[i] != tb[i]:
                data.append(unequal + " " + a + " " + unequal + " " + b)
            else:
                data.append(symbols.vbar + " " + a + " " + symbols.vbar + " " + b)

        return "\n".join(data)

    # a_text -> clean full received
    # b_text -> clean full expected
    # first_failure -> index of the first line unmatched 
    @staticmethod
    def first_failure_diff(a_text: str, b_text: str, first_failure) -> str:
        def get(vet, index):
            if index < len(vet):
                return vet[index]
            return ""

        a_render = Diff.render_white(a_text).splitlines()
        b_render = Diff.render_white(b_text).splitlines()

        first_a = get(a_render, first_failure)
        first_b = get(b_render, first_failure)
        greater = max(Colored.len(first_a), Colored.len(first_b))
        lbefore = ""

        if first_failure > 0:
            lbefore = Colored.remove_colors(get(a_render, first_failure - 1))
            greater = max(greater, Colored.len(lbefore))

        out_a, out_b = Diff.colorize_2_lines_diff(first_a, first_b)

        postext  = symbols.vbar + " " + Colored.ljust(out_a, greater) + Colored.paint(" (expected)", Color.GREEN) + "\n"
        postext += symbols.vbar + " " + Colored.ljust(out_b, greater) + Colored.paint(" (received)", Color.RED) + "\n"
        postext += symbols.vbar + " " + Colored.ljust(Diff.make_line_arrow_up(first_a, first_b), greater) + Colored.paint(" (mismatch)", Color.BLUE) + "\n"
        return postext

    @staticmethod
    def find_first_mismatch(line_a: str, line_b: str) -> int: 
        i = 0
        while i < len(line_a) and i < len(line_b):
            if line_a[i] != line_b[i]:
                return i
            i += 1
        return i
    
    @staticmethod
    def colorize_2_lines_diff(line_a: str, line_b: str, neutral:Color=Color.WHITE, expected:Color=Color.GREEN, received:Color=Color.RED) -> Tuple[str, str]:
        pos = Diff.find_first_mismatch(line_a, line_b)
        a_out = Colored.paint(line_a[0:pos], neutral) + Colored.paint(line_a[pos:], expected)
        b_out = Colored.paint(line_b[0:pos], neutral) + Colored.paint(line_b[pos:], received)
        return (a_out, b_out)
    
    

    # return a tuple of two strings with the diff and the index of the  first mismatch line
    @staticmethod
    def render_diff(a_text: str, b_text: str, pad: Optional[bool] = None) -> Tuple[List[str], List[str], int]:
        a_lines = a_text.splitlines()
        b_lines = b_text.splitlines()

        a_output = []
        b_output = []

        a_size = len(a_lines)
        b_size = len(b_lines)
        
        first_failure = -1

        cut: int = 0
        if pad is True:
            cut = (Report.get_terminal_size() - 6)// 2

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
            a_data = get(a_lines, i)
            b_data = get(b_lines, i)
            
            if i >= a_size or i >= b_size or a_lines[i] != b_lines[i]:
                if first_failure == -1:
                    first_failure = i
                a_out, b_out = Diff.colorize_2_lines_diff(a_data, b_data, Color.YELLOW)
                a_output.append(a_out)
                b_output.append(b_out)
            else:
                a_output.append(a_data)
                b_output.append(b_data)

        return a_output, b_output, first_failure

    @staticmethod
    def mount_up_down_diff(unit: Unit) -> str:
        output = io.StringIO()

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        dotted = "-"

        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received)
        string_input = "\n".join([symbols.vbar + " " + line for line in string_input.split("\n")])[0:-2]
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR:
            unequal = symbols.vbar
        expected_lines, received_lines = Diff.put_left_equal(expected_lines, received_lines, unequal)

        output.write(Report.centralize("", symbols.hbar, "╭") + "\n")
        output.write(Report.centralize(str(unit), " ", symbols.vbar) + "\n")
        output.write(Report.centralize(Colored.paint(" INPUT ", Color.BLUE), symbols.hbar, "├") + "\n")
        output.write(string_input)
        output.write(Report.centralize(Colored.paint(" EXPECTED ", Color.GREEN), symbols.hbar, "├") + "\n")
        output.write("\n".join(expected_lines) + "\n")
        output.write(Report.centralize(Colored.paint(" RECEIVED ", Color.RED), symbols.hbar, "├") + "\n")
        output.write("\n".join(received_lines) + "\n")
        if unit.result != ExecutionResult.EXECUTION_ERROR:
            output.write(Report.centralize(Colored.paint(" WHITESPACE ", Color.BOLD),  symbols.hbar, "├") + "\n")
            output.write(Diff.first_failure_diff(string_expected, string_received, first_failure))
        output.write(Report.centralize("",  symbols.hbar, "╰") + "\n")

        return output.getvalue()

    @staticmethod
    def put_left_equal(exp_lines: str, rec_lines: str, unequal:str=symbols.unequal):

        max_size = max(len(exp_lines), len(rec_lines))

        for i in range(max_size):
            if i >= len(exp_lines) or i >= len(rec_lines) or (exp_lines[i] != rec_lines[i]):
                exp_lines[i] = unequal + " " + exp_lines[i]
                rec_lines[i] = unequal + " " + rec_lines[i]
            else:
                exp_lines[i] = symbols.vbar + " " + exp_lines[i]
                rec_lines[i] = symbols.vbar + " " + rec_lines[i]
        
        return exp_lines, rec_lines
            

    @staticmethod
    def mount_side_by_side_diff(unit: Unit) -> str:

        def title_side_by_side(left, right, filler=" ", middle=" ", prefix=""):
            half = int((Report.get_terminal_size() - len(middle)) / 2)
            line = ""
            a = Colored.center(left, half, filler)
            if Colored.len(a) > half:
                a = a[:half]
            line += a
            line += middle
            b = Colored.center(right, half, filler)
            if Colored.len(b) > half:
                b = b[:half]
            line += b
            if prefix != "":
                line = prefix + line[1:]
            return line

        output = io.StringIO()

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        dotted = "-"
        vertical_separator = symbols.vbar
        hbar = symbols.hbar

        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received, True)
        output.write(Report.centralize("", hbar, "╭") + "\n")
        output.write(Report.centralize(str(unit), " ", "│") + "\n")
        input_header = Colored.paint(" INPUT ", Color.BLUE)
        output.write(title_side_by_side(input_header, input_header, hbar, "┬", "├") + "\n")
        if (string_input != ""):
            output.write(Diff.side_by_side(string_input.split("\n")[:-1], string_input.split("\n")[:-1]) + "\n")
        expected_header = Colored.paint(" EXPECTED ", Color.GREEN)
        received_header = Colored.paint(" RECEIVED ", Color.RED)
        output.write(title_side_by_side(expected_header, received_header, hbar, "┼", "├") + "\n")
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR:
            unequal = symbols.vbar
        output.write(Diff.side_by_side(expected_lines, received_lines, unequal) + "\n")
        if unit.result != ExecutionResult.EXECUTION_ERROR:
            output.write(Report.centralize(Colored.paint(" WHITESPACE ", Color.BOLD),  symbols.hbar, "├") + "\n")
            output.write(Diff.first_failure_diff(string_expected, string_received, first_failure))
        output.write(Report.centralize("",  symbols.hbar, "╰") + "\n")

        return output.getvalue()

