import curses
from tko.util.rtext import RText
from tko.widget.colors import Colors
from tko.i18n import MsgKey, t


class TextPosition:
    def __init__(self, y: int, x: int, text: RText):
        self.y = y
        self.x = x
        self.text = text

    def __str__(self):
        return f"{self.y}:{self.x}:{self.text}"

    
class TokenPosition:
    def __init__(self, y: int, x: int, style: str, text: str):
        self.y = y
        self.x = x
        self.style = style
        self.text = text

    def __str__(self):
        return f"{self.y}:{self.x}:({self.style}:{self.text})"


class Fmt:
    __scr = None
    color_pairs: dict[str, int] = {}

    COLOR_MAP = {
        'k': curses.COLOR_BLACK,
        'r': curses.COLOR_RED,
        'g': curses.COLOR_GREEN,
        'y': curses.COLOR_YELLOW,
        'b': curses.COLOR_BLUE,
        'm': curses.COLOR_MAGENTA,
        'c': curses.COLOR_CYAN,
        'w': curses.COLOR_WHITE
    }

    @staticmethod
    def set_scr(scr: curses.window):
        Fmt.__scr = scr
        Fmt.init_colors()

    @staticmethod
    def init_colors():
        pair_number = 1
        curses.start_color()
        curses.use_default_colors()
        for fk, fg in Fmt.COLOR_MAP.items():
            if fk == "T":
                continue
            curses.init_pair(pair_number, fg, -1)
            Fmt.color_pairs[fk] = pair_number
            pair_number += 1

        for fk, fg in Fmt.COLOR_MAP.items():
            for bk, bg in Fmt.COLOR_MAP.items():
                curses.init_pair(pair_number, fg, bg)
                Fmt.color_pairs[fk + bk.upper()] = pair_number
                pair_number += 1

    @staticmethod
    def stroke(y: int, x: int, fmt: str, text: str):
        if Fmt.__scr is None:
            raise Exception(t(MsgKey.FMT_NOT_INITIALIZED))
        stdscr = Fmt.__scr
        italic = False
        underline = False
        reverse = False
        source_fmt = fmt
        if "X" in fmt or "x" in fmt:
            reverse = True
            fmt = fmt.replace("X", "").replace("x", "")
        if "/" in fmt:
            italic = True
            fmt = fmt.replace("/", "")
        if "_" in fmt:
            underline = True
            fmt = fmt.replace("_", "")

        fg_list = [c for c in fmt if c.islower()]
        bg_list = [c for c in fmt if c.isupper()]
        bg = "" if len(bg_list) == 0 else bg_list[0]
        fg = "" if len(fg_list) == 0 else fg_list[0]

        if bg != "" and fg == "":
            fg = "k"
        if fg == "" and bg == "":
            pair_number = -1
        else:
            try:
                pair_number = Fmt.color_pairs[fg + bg]
            except KeyError:
                raise(Exception("Cor não encontrada: " + source_fmt))
        if italic:
            stdscr.attron(curses.A_ITALIC)
        if underline:
            stdscr.attron(curses.A_UNDERLINE)
        if reverse:
            stdscr.attron(curses.A_REVERSE)
        if pair_number != -1:
            stdscr.attron(curses.color_pair(pair_number))
        try:
            stdscr.addstr(y, x, text)
        except curses.error as _e:
            lines, cols = Fmt.get_size()
            if y == lines - 1:
                if x + len(text) <= cols:
                    pass
        except ValueError as _e:
            pass
        if pair_number != -1:
            stdscr.attroff(curses.color_pair(pair_number))
        if italic:
            stdscr.attroff(curses.A_ITALIC)
        if underline:
            stdscr.attroff(curses.A_UNDERLINE)
        if reverse:
            stdscr.attroff(curses.A_REVERSE)

    @staticmethod
    def cut_box(y: int, x: int, box_y: int, box_x: int, sentence: RText) -> list[TextPosition]:
        lines: list[RText] = sentence.split("\n")
        output: list[TextPosition] = []
        for line in lines:
            px = x
            if y < 0:
                y += 1
                continue
            if y >= box_y:
                break
            if px < 0:
                line = line.slice(-px)
                px = 0
            if px + len(line) > box_x:
                line = line.slice(0, box_x - px)
            output.append(TextPosition(y, px, line))
            y += 1
        return output

    @staticmethod
    def split_in_tokens(text_lines: list[TextPosition]) -> list[TokenPosition]:
        output: list[TokenPosition] = []
        for text_pos in text_lines:
            y = text_pos.y
            x = text_pos.x
            line = text_pos.text
            for style, text in line.runs:
                output.append(TokenPosition(y, x, style, text))
                x += len(text)
        return output

    @staticmethod
    def write(y: int, x: int, sentence: RText | str):
        if isinstance(sentence, str):
            data = RText(sentence)
        else:
            data = sentence

        lines, cols = Fmt.get_size()
        text_lines = Fmt.cut_box(y, x, lines, cols, data)
        token_list = Fmt.split_in_tokens(text_lines)
        for token_pos in token_list:
            y = token_pos.y
            x = token_pos.x
            Fmt.stroke(y, x, token_pos.style, token_pos.text)

    @staticmethod
    def get_percent(value: int, pad: int = 0) -> RText:
        colors = Colors()
        text = f"{str(value)}%".rjust(pad)
        if value == 100:
            return RText("100%", colors.mark_complete)
        if value >= 70:
            return RText(text, colors.mark_required)
        if value == 0:
            return RText(text, colors.mark_nothing)
        return RText(text, colors.mark_started)
    
    @staticmethod
    def get_screen() -> curses.window:
        if Fmt.__scr is None:
            raise Exception("Fmt.__scr não foi inicializado")
        return Fmt.__scr

    @staticmethod
    def getch():
        return Fmt.get_screen().getch()

    @staticmethod
    def clear():
        Fmt.get_screen().erase()

    @staticmethod
    def refresh():
        Fmt.get_screen().refresh()

    @staticmethod
    def get_size() -> tuple[int, int]:
        return Fmt.get_screen().getmaxyx()


def test_fmt(scr: curses.window):
    curses.curs_set(0)
    Fmt.init_colors()
    Fmt.set_scr(scr)

    output = RText("..")
    for i in range(60):
        output += RText(str(i) + " ", "r")
    for i in range(15):
        Fmt.write(i - 2, -1, output)
    scr.getch()
