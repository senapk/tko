from .fmt import Fmt
from ..util.sentence import Sentence



class Frame:
    def __init__(self, y: int = 0, x: int = 0):
        self._x = x
        self._y = y
        self._inner_dx = 0
        self._inner_dy = 0
        self._border = "rounded"
        self._filled = False
        self._header: Sentence = Sentence()
        self._header_align = ""
        self._footer: Sentence = Sentence()
        self._footer_align = ""
        self._fill_char = " "

    def set_pos(self, y: int, x: int):
        self._x = x
        self._y = y
        return self

    def set_inner(self, inner_dy: int, inner_dx: int):
        self._inner_dy = inner_dy
        self._inner_dx = inner_dx
        return self
    
    def get_inner(self):
        return (self._inner_dy, self._inner_dx)

    def set_end(self, y: int, x: int):
        self._inner_dx = x - self._x - 1
        self._inner_dy = y - self._y - 1
        # Fmt.write(0, 0, Sentence().addt(f"{self._inner_w}, {self._inner_h}"))
        # Fmt.getch()
        return self
    
    def set_fill_char(self, char: str):
        self._fill_char = char
        return self
    
    def get_symbol(self, value: str):
        square = { "lu": "┌", "ru": "┐", "ld": "└", "rd": "┘", "h": "─", "v": "│" }
        rounded = { "lu": "╭", "ru": "╮", "ld": "╰", "rd": "╯", "h": "─", "v": "│" }
        bold = { "lu": "┏", "ru": "┓", "ld": "┗", "rd": "┛", "h": "━", "v": "┃" }

        if self._border == "square":
            return square[value]
        elif self._border == "rounded":
            return rounded[value]
        elif self._border == "bold":
            return bold[value]
        return " "
        
    def set_border_none(self):
        self._border = "none"
        return self
        
    def set_border_bold(self):
        self._border = "bold"
        return self

    def set_border_rounded(self):
        self._border = "rounded"
        return self

    def set_border_square(self):
        self._border = "square"
        return self
 
    def set_header(self, header: Sentence, align="<"):
        self._header_align = align
        self._header = header
        return self

    def set_footer(self, footer: Sentence, align=">"):
        self._footer_align = align
        self._footer = footer
        return self

    def set_fill(self):
        self._filled = True
        return self

    def set_nofill(self):
        self._filled = False
        return self
    
    def write(self, y: int, x: int, sentence: Sentence) -> bool:
        lines, cols = Fmt.get_size()

        x_min = max(-1, self._x)
        y_min = max(-1, self._y)
        x_max = min(cols, self._x + self._inner_dx)
        y_max = min(lines, self._y + self._inner_dy)

        x_abs = x + self._x + 1
        y_abs = y + self._y + 1

        count = 0

        if y_abs <= y_min or y_abs > y_max:
            return False

        for token in sentence.get():
            fmt, text = token.fmt, token.text
            if x_abs - 1 < x_min: # Se o texto começa fora do frame
                if x_abs + len(text) > x_min: # mas ter parte dentro
                    text = text[x_min - x_abs + 1:]
                    x_abs = x_min + 1

            if x_abs <= x_max: # Se o texto começa dentro do frame
                if x_abs + len(text) >= x_max:
                    text = text[:x_max - x_abs + 1]
                Fmt.stroke(y_abs, x_abs, fmt, text)
                count += 1
            x_abs += len(text)
        return False if count == 0 else True

    def draw(self):
        x = self._x
        y = self._y
        dx = self._inner_dx
        dy = self._inner_dy
        up_left = self.get_symbol("lu")
        up_right = self.get_symbol("ru")
        down_left = self.get_symbol("ld")
        down_right = self.get_symbol("rd")
        hor = self.get_symbol("h")
        ver = self.get_symbol("v")
        header = self._header
        footer = self._footer
        if self._footer_align == "<":
            footer.ljust(dx - 2, hor)
        elif self._footer_align == ">":
            footer.rjust(dx - 2, hor)
        else:
            footer.center(dx - 2, hor) 
    
        if self._header_align == "<":
            header.ljust(dx - 2, hor)
        elif self._header_align == ">":
            header.rjust(dx - 2, hor)
        else:
            header.center(dx - 2, hor)

        above = Sentence().addt(up_left + hor).concat(header).addt(hor + up_right)
        below = Sentence().addt(down_left + hor).concat(footer).addt(hor + down_right)
        
        Fmt.write(y, x, above)
        Fmt.write(y + dy + 1, x, below)
        if self._filled:
            for i in range(1, dy + 1):
                Fmt.write(y + i, x, Sentence().addt(ver + dx * self._fill_char + ver))
        else:
            for i in range(1, dy + 1):
                Fmt.write(y + i, x, Sentence().addt(ver))
                Fmt.write(y + i, x + dx + 1, Sentence().addt(ver))
        return self
