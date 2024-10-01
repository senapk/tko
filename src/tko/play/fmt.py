import curses
from typing import Dict, Tuple
from tko.util.text import Text, Token
from tko.play.colors import Colors

class TextPosition:
    def __init__(self, y: int, x: int, text: Text):
        self.y = y
        self.x = x
        self.text = text

    def __str__(self):
        return f"{self.y}:{self.x}:{self.text}"
    
class TokenPosition:
    def __init__(self, y: int, x: int, token: Token):
        self.y = y
        self.x = x
        self.token = token

    def __str__(self):
        return f"{self.y}:{self.x}:{self.token}"

class Fmt:
    __scr = None
    # Definindo constantes para as cores
    color_pairs: Dict[str, int] = {}

    COLOR_MAP = {
        'k': curses.COLOR_BLACK,
        'r': curses.COLOR_RED,
        'g': curses.COLOR_GREEN,
        'y': curses.COLOR_YELLOW,
        'b': curses.COLOR_BLUE,
        'm': curses.COLOR_MAGENTA,
        'c': curses.COLOR_CYAN,
        'w': curses.COLOR_WHITE,
    }
    @staticmethod
    def set_scr(scr):
        Fmt.__scr = scr
        Fmt.init_colors()

    @staticmethod
    def init_colors():
        pair_number = 1
        curses.start_color()
        curses.use_default_colors()
        for fk, fg in Fmt.COLOR_MAP.items():
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
            raise Exception("Fmt.__scr não foi inicializado")
        stdscr = Fmt.__scr
        italic = False
        underline = False
        source_fmt = fmt
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
                # print("Cor não encontrada: " + fg + bg)
                raise(Exception("Cor não encontrada: " + source_fmt))
                exit(1)
        if italic:
            stdscr.attron(curses.A_ITALIC)
        if underline:
            stdscr.attron(curses.A_UNDERLINE)
        # Exibir o texto com a combinação de cores escolhida
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
            # lines, cols = stdscr.getmaxyx()
            # stdscr.addstr(10, 10, f"y:{y}, x:{x}, fmt:{fmt}, len:{len(text)} lines:{lines}, cols:{cols}")
            # stdscr.addstr(1, 0, text)
            # raise Exception(f"y:{y}, x:{x}, fmt:{fmt}, len:{len(text)} lines:{lines}, cols:{cols}\n{text}")
        if pair_number != -1:
            stdscr.attroff(curses.color_pair(pair_number))
        if italic:
            stdscr.attroff(curses.A_ITALIC)
        if underline:
            stdscr.attroff(curses.A_UNDERLINE)

    # break in lines and cut everything that is out of the box
    @staticmethod
    def cut_box(y: int, x: int, box_y: int, box_x: int, sentence: Text) -> list[TextPosition]:
        lines: list[Text] = sentence.split("\n")
        output: list[TextPosition] = []
        for line in lines:
            px = x
            if y < 0:
                y += 1
                continue
            if y >= box_y:
                break
            if px < 0:
                line.data = line.data[-px:]
                px = 0
            if px + len(line) > box_x:
                line.data = line.data[:box_x - px]
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
            for token in line.resume():
                output.append(TokenPosition(y, x, token))
                x += len(token)
        return output

    @staticmethod
    def write(y: int, x: int, sentence: Text | str):
        if isinstance(sentence, str):
            data: Text = Text().add(sentence)
        else:
            data = sentence

        lines, cols = Fmt.get_size()
        text_lines = Fmt.cut_box(y, x, lines, cols, data)
        token_list = Fmt.split_in_tokens(text_lines)
        for token_pos in token_list:
            y = token_pos.y
            x = token_pos.x
            token = token_pos.token
            # print(f"y:{y}, x:{x}, fmt:{token.fmt}, len:{len(token.text)}")
            Fmt.stroke(y, x, token.fmt, token.text)

    # @staticmethod
    # def get_user_input(stdscr, prompt: str) -> str:
    #     lines, cols = stdscr.getmaxyx()
    #     curses.echo()  # Ativa a exibição dos caracteres digitados
    #     curses.curs_set(1)  # Ativa o cursor
    #     stdscr.addstr(0, 0, cols * " ")
    #     stdscr.addstr(0, 0, prompt)
    #     stdscr.refresh()
    #     input_str = stdscr.getstr(0, len(prompt), 20).decode('utf-8')  # Captura o input do usuário
    #     curses.noecho()  # Desativa a exibição dos caracteres digitados
    #     curses.curs_set(0)
    #     return input_str

    @staticmethod
    def get_percent(value, pad = 0) -> Text:
        text = f"{str(value)}%".rjust(pad)
        if value == 100:
            return Text().addf(Colors.mark_complete, "100%")
        if value >= 70:
            return Text().addf(Colors.mark_required, text)
        if value == 0:
            return Text().addf(Colors.mark_nothing, text)
        return Text().addf(Colors.mark_started, text)
    
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
    def get_size() -> Tuple[int, int]:
        return Fmt.get_screen().getmaxyx()
        

def test_fmt(scr):
    curses.curs_set(0)  # Esconde o cursor
    Fmt.init_colors()  # Inicializa as cores
    Fmt.set_scr(scr)  # Define o scr como global

    output = Text("..")
    for i in range(60):
        output.addf("r", str(i) + " ")
    for i in range(15):
        Fmt.write(i - 2, -1, output)
    scr.getch()

if __name__ == "__main__":
    curses.wrapper(test_fmt)
    # values = Fmt.cut_box(-2, -1, 10, 10, Text().add("1234\n56\n789").addf("r", "1\n23").addf("g", "456"))
    # print([str(v) for v in values])
    # tokens = Fmt.split_in_tokens(values)
    # print(", ".join([str(v) for v in tokens]))