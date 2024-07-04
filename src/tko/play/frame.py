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
        self._wrap = False
        self._border_color = ""
        self._print_index = 0

    def set_border_color(self, color: str):
        self._border_color = color

    def get_dx(self):
        return self._inner_dx
    
    def get_dy(self):
        return self._inner_dy
    
    def get_x(self):
        return self._x

    def get_y(self):
        return self._y
    
    def get_header(self):
        return self._header
    
    def get_footer(self):
        return self._footer

    def set_pos(self, y: int, x: int):
        self._x = x
        self._y = y
        return self

    def set_size(self, size_y, size_x):
        self._inner_dx = size_x - 2
        self._inner_dy = size_y - 2
        return self

    def set_inner(self, inner_dy: int, inner_dx: int):
        self._inner_dy = inner_dy
        self._inner_dx = inner_dx
        return self
    
    def get_inner(self):
        return (self._inner_dy, self._inner_dx)

    def get_size(self):
        return self._inner_dy + 2, self._inner_dx + 2

    def set_end(self, y: int, x: int):
        self._inner_dx = x - self._x - 1
        self._inner_dy = y - self._y - 1
        # Fmt.write(0, 0, Sentence().addt(f"{self._inner_w}, {self._inner_h}"))
        # Fmt.getch()
        return self
    
    def set_wrap(self):
        self._wrap = True

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
    
    def print(self, x: int, sentence: Sentence):
        self.write(self._print_index, x, sentence)
        self._print_index += 1
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
                missing = ""
                if x_abs + len(text) >= x_max:
                    cut_point = x_max - x_abs + 1
                    missing = text[cut_point:]
                    text = text[:cut_point]

                Fmt.stroke(y_abs, x_abs, fmt, text)

                if self._wrap and missing != "":
                    Fmt.stroke(y_abs + 1, x_abs, missing)
                count += 1
            x_abs += len(text)
        return False if count == 0 else True

    def draw(self):
        x = self._x
        y = self._y
        dx = self._inner_dx
        dy = self._inner_dy
        color = self._border_color
        up_left = self.get_symbol("lu")
        up_right = self.get_symbol("ru")
        down_left = self.get_symbol("ld")
        down_right = self.get_symbol("rd")
        hor = self.get_symbol("h")
        ver = self.get_symbol("v")
        header = self._header
        footer = self._footer
        if self._footer_align == "<":
            footer.ljust(dx, hor, color)
        elif self._footer_align == ">":
            footer.rjust(dx, hor, color)
        else:
            footer.center(dx, hor, color) 
    
        if self._header_align == "<":
            header.ljust(dx, hor, color)
        elif self._header_align == ">":
            header.rjust(dx, hor, color)
        else:
            header.center(dx, hor, color)

        above = Sentence().addf(color, up_left).concat(header).addf(color, up_right)
        below = Sentence().addf(color, down_left).concat(footer).addf(color, down_right)
        
        Fmt.write(y, x, above)
        Fmt.write(y + dy + 1, x, below)
        if self._filled:
            for i in range(1, dy + 1):
                Fmt.write(y + i, x, Sentence().addf(color, ver).addt(dx * self._fill_char).addf(color, ver))
        else:
            for i in range(1, dy + 1):
                Fmt.write(y + i, x, Sentence().addf(color, ver))
                Fmt.write(y + i, x + dx + 1, Sentence().addf(color, ver))
        return self
