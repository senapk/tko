from tko.util.symbols import symbols
from tko.util.text import Text

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
                    hdiff += symbols.arrow_up
                    return hdiff
            else:
                hdiff += " "
            i += 1
        while len(hdiff) < lim:
            hdiff += " "
        return hdiff

    @staticmethod
    def render_white(text: str) -> str:
        return text.replace(' ', symbols.whitespace.text).replace('\n', symbols.newline.text)

    def first_failure_diff(self, a_text: str, b_text: str | None, first_failure: int) -> list[Text]:
        if b_text is None:
            b_text = ""
        def get(vet: list[str], index: int) -> str:
            if 0 <= index < len(vet):
                return DiffBuilder.render_white(vet[index])
            return ""

        a_render = a_text.splitlines(True)
        b_render = b_text.splitlines(True)
        first_a = get(a_render, first_failure)
        first_b = get(b_render, first_failure)
        out_a, out_b = DiffBuilder.colorize_2_lines_diff(first_a, first_b)
        if out_a is None:
            out_a = Text()
        if out_b is None:
            out_b = Text()
        greater = max(len(out_a), len(out_b))
        output: list[Text] = []
        width = self.width - 13
        output.append(Text().add(" ").add(out_a.ljust(greater)).trim_end(width).addf("y", " (esperado)"))
        output.append(Text().add(" ").add(out_b.ljust(greater)).trim_end(width).addf("r", " (recebido)"))
        diff = DiffBuilder.make_line_arrow_up(first_a, first_b)
        output.append(Text().add(" ").add(diff.ljust(greater)).trim_end(width).addf("b", " (primeiro)"))
        return output

    @staticmethod
    def colorize_2_lines_diff(la: str | None, lb: str | None, neut: str = "g", exp: str = "y", rec: str = "r") -> tuple[Text | None, Text | None]:
        pos = DiffBuilder.find_first_mismatch(la, lb)
        tla: Text | None = None
        tlb: Text | None = None
        if la is not None:
            tla = Text().addf(neut, la[0:pos]).addf(exp, la[pos:])
        if lb is not None:
            tlb = Text().addf(neut, lb[0:pos]).addf(rec, lb[pos:])
        return tla, tlb

    @staticmethod
    def find_first_mismatch(line_a: str | None, line_b: str | None) -> int: 
        if line_a is None or line_b is None:
            return 0
        i = 0
        while i < len(line_a) and i < len(line_b):
            if line_a[i] != line_b[i]:
                return i
            i += 1
        return i

    # return a tuple of two strings with the diff and the index of the first mismatch line
    @staticmethod
    def render_diff(a_text: str | None, b_text: str | None) -> tuple[list[tuple[Text | None, Text | None]], int]:
        if a_text is None:
            a_text = ""
        if b_text is None:
            b_text = ""
        a_lines: list[str] = a_text.splitlines(keepends=True)
        b_lines: list[str] = b_text.splitlines(keepends=True)
        output: list[tuple[Text | None, Text | None]] = []
        a_size = len(a_lines)
        b_size = len(b_lines)
        first_failure = -1
        max_size = max(a_size, b_size)

        # lambda function to return element in index i or empty if out of bounds
        def get_without_newline(vet: list[str], index: int) -> str | None:
            if index < len(vet):
                data = vet[index]
                if data.endswith("\n"):
                    data = data[:-1]
                return data
            return None
        
        expected_color = "y"
        received_color = "r" if a_text != "" else ""
        for i in range(max_size):
            if i >= a_size or i >= b_size or a_lines[i] != b_lines[i]:
                if first_failure == -1:
                    first_failure = i
            a_data: str | None = get_without_newline(a_lines, i)
            b_data: str | None = get_without_newline(b_lines, i)
            a_out, b_out = DiffBuilder.colorize_2_lines_diff(a_data, b_data, "g", expected_color, received_color)
            output.append((a_out, b_out))
        return output, first_failure
