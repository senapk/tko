from typing import List, Optional, Tuple

from ..util.symbols import symbols
from ..util.text import Text, Token
from ..util.consts import ExecutionResult
from .unit import Unit
from ..util.raw_terminal import RawTerminal

class DiffBuilder:

    vinput    = " INSERIDO "
    vexpected = " ESPERADO "
    vreceived = " RECEBIDO "
    vunequal  = " DESIGUAL "

    @staticmethod
    def make_line_arrow_up(a: str, b: str) -> Text:
        hdiff = Text()
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
        while len(hdiff) < lim:
            hdiff += " "
        return hdiff

    @staticmethod
    def render_white(text: Text, color: str = "") -> Optional[Text]:
        out = Text().add(text).replace(' ', Token(symbols.whitespace.text, color)).replace('\n', Token(symbols.newline.text, color))

        return out

    # create a string with both ta and tb side by side with a vertical bar in the middle
    @staticmethod
    def side_by_side(ta: List[Text], tb: List[Text], unequal: Token = symbols.unequal) -> List[Text]:
        cut = (RawTerminal.get_terminal_size() - 6) // 2
        upper = max(len(ta), len(tb))
        data: List[Text] = []

        for i in range(upper):
            a = ta[i] if i < len(ta) else Text("###############")
            b = tb[i] if i < len(tb) else Text("###############")
            if len(a) < cut:
                a = a.ljust(cut, Token(" "))
            if i >= len(ta) or i >= len(tb) or ta[i] != tb[i]:
                data.append(Text() + unequal + " " + a + " " + unequal + " " + b + " " + symbols.vbar)
            else:
                data.append(Text() + symbols.vbar + " " + a + " " + symbols.vbar + " " + b + " " + symbols.vbar)

        return data

    # a_text -> clean full received
    # b_text -> clean full expected
    # first_failure -> index of the first line unmatched 
    @staticmethod
    def first_failure_diff(a_text: str, b_text: str, first_failure: int) -> List[Text]:
        def get(vet, index):
            if index < len(vet):
                return DiffBuilder.render_white(vet[index])
            return ""

        a_render = a_text.splitlines(True)
        b_render = b_text.splitlines(True)

        first_a = get(a_render, first_failure)
        first_b = get(b_render, first_failure)
        # greater = max(len(first_a), len(first_b))

        # if first_failure > 0:
        #     lbefore = get(a_render, first_failure - 1)
        #     greater = max(greater, len(lbefore))

        out_a, out_b = DiffBuilder.colorize_2_lines_diff(Text(first_a), Text(first_b))
        greater = max(len(out_a), len(out_b))
        output: List[Text] = []
        width = RawTerminal.get_terminal_size() - 13
        output.append(Text().add(" ").add(out_a.ljust(greater)).trim_end(width).addf("g", " (esperado)"))
        output.append(Text().add(" ").add(out_b.ljust(greater)).trim_end(width).addf("r", " (recebido)"))
        diff = DiffBuilder.make_line_arrow_up(first_a, first_b)
        output.append(Text().add(" ").add(diff.ljust(greater)).trim_end(width).addf("b", " (primeiro)"))
        return output

    @staticmethod
    def find_first_mismatch(line_a: Text, line_b: Text) -> int: 
        i = 0
        while i < len(line_a) and i < len(line_b):
            if line_a[i] != line_b[i]:
                return i
            i += 1
        return i
    
    @staticmethod
    def colorize_2_lines_diff(la: Text, lb: Text, neut: str = "", exp: str = "g", rec: str = "r") -> Tuple[Text, Text]:
        pos = DiffBuilder.find_first_mismatch(la, lb)
        lat = la.get_text()
        lbt = lb.get_text()
        a_out = Text().addf(neut, lat[0:pos]).addf(exp, lat[pos:])
        b_out = Text().addf(neut, lbt[0:pos]).addf(rec, lbt[pos:])
        return a_out, b_out

    # return a tuple of two strings with the diff and the index of the  first mismatch line
    @staticmethod
    def render_diff(a_text: str, b_text: str, pad: Optional[bool] = None) -> Tuple[List[Text], List[Text], int]:
        a_lines = a_text.splitlines()
        b_lines = b_text.splitlines()

        a_output: List[Text] = []
        b_output: List[Text] = []

        a_size = len(a_lines)
        b_size = len(b_lines)
        
        first_failure = -1

        cut: int = 0
        if pad is True:
            cut = (RawTerminal.get_terminal_size() - 6) // 2

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
        expected_color = "g"
        received_color = "r" if a_text != "" else ""
        for i in range(max_size):
            a_data = Text(get(a_lines, i))
            b_data = Text(get(b_lines, i))
            
            if i >= a_size or i >= b_size or a_lines[i] != b_lines[i]:
                if first_failure == -1:
                    first_failure = i
                a_out, b_out = DiffBuilder.colorize_2_lines_diff(a_data, b_data, "y", expected_color, received_color)
                a_output.append(a_out)
                b_output.append(b_out)
            else:
                a_output.append(a_data)
                b_output.append(b_data)

        return a_output, b_output, first_failure

    @staticmethod
    def mount_up_down_diff(unit: Unit, curses=False) -> List[Text]:
        output: List[Text] = []

        width = RawTerminal.get_terminal_size() - 1

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        no_diff_mode = string_input == "" and string_expected == ""

        if string_received is None:
            string_received = ""
        expected_lines, received_lines, first_failure = DiffBuilder.render_diff(string_expected, string_received)
        string_input_list = [Text().add(symbols.vbar.text).add(" ").add(line) for line in string_input.split("\n")][:-1]
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR or unit.result == ExecutionResult.COMPILATION_ERROR or string_expected == "":
            unequal = symbols.vbar
        expected_lines, received_lines = DiffBuilder.put_left_equal(expected_lines, received_lines, unequal)

        color = "b" if string_expected != string_received else "g"
        if not curses:
            output.append(RawTerminal.centralize("", symbols.hbar, "╭", "╮"))
            output.append(RawTerminal.centralize(unit.str(), " ", symbols.vbar, symbols.vbar))
            output.append(RawTerminal.centralize(Text().addf(color, DiffBuilder.vinput), symbols.hbar, "├", "┤"))
        else:
            if no_diff_mode:
                output.append(RawTerminal.centralize(Text().addf(color, DiffBuilder.vreceived), symbols.hbar, "╭"))
            else:
                output.append(RawTerminal.centralize(Text().addf(color, DiffBuilder.vinput), symbols.hbar, "╭"))

        for line in string_input_list:
            output.append(line.ljust(width, Token(" ")).add(symbols.vbar))

        if string_expected != "":
            output.append(RawTerminal.centralize(Text().addf("g", DiffBuilder.vexpected), symbols.hbar, "├", "┤"))
            for line in expected_lines:
                output.append(line.ljust(width, Token(" ")).add(symbols.vbar))
            
        # output.append("\n".join(expected_lines))
        rcolor = "r" if (string_expected != "" and string_expected != string_received) else "g"
        if no_diff_mode == False:
            output.append(RawTerminal.centralize(Text().addf(rcolor, DiffBuilder.vreceived), symbols.hbar, "├", "┤"))
        
        for line in received_lines:
            output.append(line.ljust(width, Token(" ")).trim_end(width).add(symbols.vbar))

        include_rendering = False
        if string_expected != string_received and string_expected != "":
            include_rendering = True
        if unit.result == ExecutionResult.EXECUTION_ERROR or unit.result == ExecutionResult.COMPILATION_ERROR:
            include_rendering = False

        if include_rendering:
            output.append(RawTerminal.centralize(Text().addf("b", DiffBuilder.vunequal),  symbols.hbar, "├", "┤"))
            for line in DiffBuilder.first_failure_diff(string_expected, string_received, first_failure):
                output.append(Text("│").add(line).ljust(width, Token(" ")).add("│"))
        output.append(RawTerminal.centralize("",  symbols.hbar, "╰", "╯"))

        return output

    @staticmethod
    def put_left_equal(exp_lines: List[Text], rec_lines: List[Text], unequal: Token = symbols.unequal):

        max_size = max(len(exp_lines), len(rec_lines))

        for i in range(max_size):
            if i >= len(exp_lines) or i >= len(rec_lines) or (exp_lines[i] != rec_lines[i]):
                exp_lines[i] = Text() + unequal + " " + exp_lines[i]
                rec_lines[i] = Text() + unequal + " " + rec_lines[i]
            else:
                exp_lines[i] = Text() + symbols.vbar + " " + exp_lines[i]
                rec_lines[i] = Text() + symbols.vbar + " " + rec_lines[i]
        
        return exp_lines, rec_lines
            
    @staticmethod
    def title_side_by_side(left: Text, right: Text, filler: Token = Token(" "), middle: Token = Token(" "), prefix: Token = Token(), posfix: Token = Token()) -> Text:
        half = int((RawTerminal.get_terminal_size() - len(middle)) / 2)
        line = Text()
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
            line = Text() + prefix + line
        if posfix != "":
            line.data[-1].text = line.data[-1].text[:-1]
            line += posfix
        return line

    @staticmethod
    def mount_side_by_side_diff(unit: Unit, curses=False) -> List[Text]:

        output: List[Text] = []

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user
        if string_received is None:
            string_received = ""
        # dotted = "-"
        # vertical_separator = symbols.vbar
        hbar = symbols.hbar

        expected_lines, received_lines, first_failure = DiffBuilder.render_diff(string_expected, string_received, True)
        if not curses:
            output.append(RawTerminal.centralize("", hbar, "╭", "╮"))
            output.append(RawTerminal.centralize(unit.str(), " ", "│", "│"))
        input_color = "b" if string_expected != string_received else "g"
        input_headera = Text().addf(input_color, DiffBuilder.vinput)
        input_headerb = Text().addf(input_color, DiffBuilder.vinput)
        if not curses:
            output.append(DiffBuilder.title_side_by_side(input_headera, input_headerb, hbar, Token("┬"), Token("├"), Token("┤")))
        else:
            output.append(RawTerminal.centralize(Text().addf(input_color, DiffBuilder.vinput),  symbols.hbar, "╭"))
            # output.append(Diff.title_side_by_side(input_headera, input_headerb, hbar, TK("┬"), TK("╭")))

        if string_input != "":
            lines = [Text(x) for x in string_input.split("\n")[:-1]]
            output += DiffBuilder.side_by_side(lines, lines)
        expected_header = Text().addf("g", DiffBuilder.vexpected)
        rcolor = "r" if string_expected != string_received else "g"
        received_header = Text().addf(rcolor, DiffBuilder.vreceived)
        output.append(DiffBuilder.title_side_by_side(expected_header, received_header, hbar, Token("┼"), Token("├"), Token("┤")))
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR or unit.result == ExecutionResult.COMPILATION_ERROR:
            unequal = symbols.vbar
        output += DiffBuilder.side_by_side(expected_lines, received_lines, unequal)
        if unit.result != ExecutionResult.EXECUTION_ERROR and unit.result != ExecutionResult.COMPILATION_ERROR and string_expected != string_received:
            output.append(RawTerminal.centralize(Text().addf("b", DiffBuilder.vunequal),  symbols.hbar, "├", "┤"))
            for line in DiffBuilder.first_failure_diff(string_expected, string_received, first_failure):
                width = RawTerminal.get_terminal_size() - 1
                output.append(Text("│").add(line).ljust(width, Token(" ")).add("│"))
            output.append(RawTerminal.centralize("",  symbols.hbar, "╰", "╯"))
        else:
            output.append(RawTerminal.centralize("┴",  symbols.hbar, "╰", "╯"))

        return output
