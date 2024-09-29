from typing import List, Optional, Tuple

from ..util.symbols import symbols
from ..util.text import Text, Token

class DiffBuilder:
    vinput    = " INSERIDO "
    vexpected = " ESPERADO "
    vreceived = " RECEBIDO "
    vunequal  = " DESIGUAL "

    def __init__(self, width: int):
        self.width = width
        self.curses = False

    def set_curses(self):
        self.curses = True
        return self

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

    def first_failure_diff(self, a_text: str, b_text: str | None, first_failure: int) -> List[Text]:
        if b_text is None:
            b_text = ""
        def get(vet, index):
            if index < len(vet):
                return DiffBuilder.render_white(vet[index])
            return ""

        a_render = a_text.splitlines(True)
        b_render = b_text.splitlines(True)
        first_a = get(a_render, first_failure)
        first_b = get(b_render, first_failure)
        out_a, out_b = DiffBuilder.colorize_2_lines_diff(Text().add(first_a), Text().add(first_b))
        if out_a is None:
            out_a = Text()
        if out_b is None:
            out_b = Text()
        greater = max(len(out_a), len(out_b))
        output: List[Text] = []
        width = self.width - 13
        output.append(Text().add(" ").add(out_a.ljust(greater)).trim_end(width).addf("g", " (esperado)"))
        output.append(Text().add(" ").add(out_b.ljust(greater)).trim_end(width).addf("r", " (recebido)"))
        diff = DiffBuilder.make_line_arrow_up(first_a, first_b)
        output.append(Text().add(" ").add(diff.ljust(greater)).trim_end(width).addf("b", " (primeiro)"))
        return output

    @staticmethod
    def colorize_2_lines_diff(la: Text | None, lb: Text | None, neut: str = "", exp: str = "g", rec: str = "r") -> Tuple[Text | None, Text | None]:
        pos = DiffBuilder.find_first_mismatch(la, lb)
        if la is not None:
            lat = la.get_text()
            la = Text().addf(neut, lat[0:pos]).addf(exp, lat[pos:])
        if lb is not None:
            lbt = lb.get_text()
            lb = Text().addf(neut, lbt[0:pos]).addf(rec, lbt[pos:])
        return la, lb

    @staticmethod
    def find_first_mismatch(line_a: Text | None, line_b: Text | None) -> int: 
        if line_a is None or line_b is None:
            return 0
        i = 0
        while i < len(line_a) and i < len(line_b):
            if line_a[i] != line_b[i]:
                return i
            i += 1
        return i

    # return a tuple of two strings with the diff and the index of the first mismatch line
    def render_diff(self, a_text: str, b_text: str | None) -> Tuple[List[Tuple[Text | None, Text | None]], int]:
        if b_text is None:
            b_text = ""
        a_lines = a_text.splitlines()
        b_lines = b_text.splitlines()
        output: list[tuple[Text | None, Text | None]] = []
        a_size = len(a_lines)
        b_size = len(b_lines)
        first_failure = -1
        max_size = max(a_size, b_size)

        # lambda function to return element in index i or empty if out of bounds
        def get(vet, index) -> Text | None:
            if index < len(vet):
                return Text(vet[index])
            return None
        
        expected_color = "g"
        received_color = "r" if a_text != "" else ""
        for i in range(max_size):
            a_data = get(a_lines, i)
            b_data = get(b_lines, i)
            if a_data is None or b_data is None or a_data != b_data:
                if first_failure == -1:
                    first_failure = i
                a_out, b_out = DiffBuilder.colorize_2_lines_diff(a_data, b_data, "y", expected_color, received_color)
                output.append((a_out, b_out))
            else:
                output.append((a_data, b_data))
        return output, first_failure
