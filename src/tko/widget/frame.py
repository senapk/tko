from tko.widget.fmt import Fmt
from tko.util.rtext import RText
from tko.util.scrollbar import ScrollBar


class Frame:
    def __init__(self, y: int = 0, x: int = 0):
        self._x = x
        self._y = y
        self._inner_dx = 0
        self._inner_dy = 0
        self._border = "rounded"
        self._filled = False
        self._header: RText = RText()
        self._halign = ""
        self._hprefix = ""
        self._hsuffix = ""
        self._footer: RText = RText()
        self._falign = ""
        self._fprefix = ""
        self._fsuffix = ""
        self._fill_char = " "
        self._wrap = False
        self._border_color = ""
        self._print_index = 0
        self.__current_index = 0
        self.__text_length = 0
        self.__show_scrollbar = False
        self.__scrollbar_side = "left"

    def set_border_color(self, color: str):
        self._border_color = color
        return self

    def get_dx(self):
        return self._inner_dx

    def get_dy(self):
        return self._inner_dy

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def __align_header_footer(self, data: RText, symbol: str, prefix: str, suffix: str):
        dx = self._inner_dx
        color = self._border_color
        pad = dx - len(prefix) - len(suffix)
        hor = self.get_symbol("h")
        
        data = data.trim_end(pad)
        sent = RText(prefix, color) + data + RText(suffix, color)
        if symbol == "<":
            sent = sent.ljust(dx, RText(hor, color))
        elif symbol == ">":
            sent = sent.rjust(dx, RText(hor, color))
        else:
            sent = sent.center(dx, RText(hor, color))
        return sent

    def get_header(self):
        return RText(self._hprefix) + self._header + self._hsuffix
    
    def get_footer(self):
        return RText(self._fprefix) + self._footer + self._fsuffix

    def get_full_header(self):
        return self.__align_header_footer(self._header, self._halign, self._hprefix, self._hsuffix)

    def get_full_footer(self):
        return self.__align_header_footer(self._footer, self._falign, self._fprefix, self._fsuffix)

    def set_pos(self, y: int, x: int):
        self._x = x
        self._y = y
        return self

    def set_size(self, size_y: int, size_x: int):
        self._inner_dx = size_x - 2
        self._inner_dy = size_y - 2
        return self

    def set_inner(self, inner_dy: int, inner_dx: int):
        self._inner_dy = inner_dy
        self._inner_dx = inner_dx
        return self

    def get_inner(self):
        return self._inner_dy, self._inner_dx

    def get_size(self):
        return self._inner_dy + 2, self._inner_dx + 2

    def set_end(self, y: int, x: int):
        self._inner_dx = x - self._x - 1
        self._inner_dy = y - self._y - 1
        return self

    def set_wrap(self):
        self._wrap = True
        return self

    def set_fill_char(self, char: str):
        self._fill_char = char
        return self

    def get_symbol(self, value: str):
        square  = {"lu": "┌", "ru": "┐", "ld": "└", "rd": "┘", "h": "─", "v": "│"}
        rounded = {"lu": "╭", "ru": "╮", "ld": "╰", "rd": "╯", "h": "─", "v": "│"}

        if self._border == "square":
            return square[value]
        elif self._border == "rounded":
            return rounded[value]
        return " "

    def set_border_none(self):
        self._border = "none"
        return self

    def set_border_rounded(self):
        self._border = "rounded"
        return self

    def set_border_square(self):
        self._border = "square"
        return self

    def set_header(self, header: RText, align: str = "<", prefix: str = "", suffix: str = ""):
        self._halign = align
        self._header = header
        self._hprefix = prefix
        self._hsuffix = suffix
        return self

    def set_footer(self, footer: RText, align: str = ">", prefix: str = "", suffix: str = ""):
        self._falign = align
        self._footer = footer
        self._fprefix = prefix
        self._fsuffix = suffix
        return self

    def set_fill(self):
        self._filled = True
        return self

    def set_nofill(self):
        self._filled = False
        return self

    def print(self, x: int, sentence: RText):
        self.write(self._print_index, x, sentence)
        self._print_index += 1
        return self

    def write(self, y: int, x: int, sentence: RText) -> bool:
        lines, cols = Fmt.get_size()

        x_min = max(-1, self._x)
        y_min = max(-1, self._y)
        x_max = min(cols, self._x + self._inner_dx)
        y_max = min(lines, self._y + self._inner_dy)

        x_abs = x + self._x + 1
        y_abs = y + self._y + 1

        if y_abs <= y_min or y_abs > y_max:
            return False
        count = 0
        for fmt, text in sentence.runs:
            if x_abs - 1 < x_min:
                if x_abs + len(text) > x_min:
                    text = text[x_min - x_abs + 1:]
                    x_abs = x_min + 1
            if x_abs <= x_max:
                if x_abs + len(text) >= x_max:
                    cut_point = x_max - x_abs + 1
                    text = text[:cut_point]
                Fmt.stroke(y_abs, x_abs, fmt, text)
                count += 1
            x_abs += len(text)
        return count != 0

    def set_scrollbar(self, current_index: int, text_length: int, side: str = "right"):
        self.__current_index = current_index
        self.__text_length = text_length
        self.__show_scrollbar = True
        self.__scrollbar_side = side

    def __draw_scrollbar(self, current_index: int, text_length: int):
        scrollbar = ScrollBar(
            text_size=text_length,
            index=current_index,
            screen_size=self._inner_dy,
            bar_size=self._inner_dy,
            char_block="┃",
            char_empty=" ",
        )
        values = scrollbar.render()
        color = self._border_color
        for i in range(self._inner_dy):
            char = values[i] if i < len(values) else " "
            if char != " ":
                if self.__scrollbar_side == "right":
                    Fmt.stroke(self._y + 1 + i, self._x + self._inner_dx + 1, color, char)
                else:
                    Fmt.stroke(self._y + 1 + i, self._x, color, char)

    def draw(self):
        x = self._x
        y = self._y
        dx = self._inner_dx
        dy = self._inner_dy
        color = self._border_color
        up_left   = self.get_symbol("lu")
        up_right  = self.get_symbol("ru")
        down_left = self.get_symbol("ld")
        down_right = self.get_symbol("rd")
        vertical  = self.get_symbol("v")

        header = self.get_full_header()
        footer = self.get_full_footer()
        above = RText(up_left, color) + header + RText(up_right, color)
        below = RText(down_left, color) + footer + RText(down_right, color)

        if header.len() and self._border != "none":
            Fmt.write(y, x, above)
        if dy >= 0:
            Fmt.write(y + dy + 1, x, below)
        if self._filled:
            for i in range(1, dy + 1):
                Fmt.write(
                    y + i,
                    x,
                    RText(vertical, color)
                    + dx * self._fill_char
                    + RText(vertical, color),
                )
        else:
            for i in range(1, dy + 1):
                Fmt.write(y + i, x, RText(vertical, color))
                Fmt.write(y + i, x + dx + 1, RText(vertical, color))
        if self.__show_scrollbar:
            self.__draw_scrollbar(self.__current_index, self.__text_length)
        return self
