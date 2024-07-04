import curses
from typing import Dict
from ..util.sentence import Sentence
from .style import Style

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

    @staticmethod
    def write(y: int, x: int, sentence: Sentence):

        # Escreve um texto na tela com cores diferentes
        lines, cols = Fmt.get_size()
        if y < 0 or y >= lines:
            return
        for token in sentence.get():
            fmt = token.fmt
            text = token.text
            if x < 0:
                if x + len(text) >= 0:
                    text = text[-x:]
                    x = 0
            if x < cols:
                if x + len(text) >= cols:
                    text = text[:cols - x]
                Fmt.stroke(y, x, fmt, text)
            x += len(text)  # Move a posição x para a direita após o texto

    @staticmethod
    def write_text(y: int, x: int, text: str):
        Fmt.write(y, x, Sentence().addt(text))

    @staticmethod
    def debug(text: str):
        Fmt.write_text(0, 0, text)
        Fmt.getch()


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
    def get_percent(value, pad = 0) -> Sentence:
        text = f"{str(value)}%".rjust(pad)
        if value == 100:
            return Sentence().addf(Style.complete, "100%")
        if value >= 70:
            return Sentence().addf(Style.required, text)
        if value == 0:
            return Sentence().addf(Style.nothing, text)
        return Sentence().addf(Style.started, text)
    
    @staticmethod
    def getch():
        if Fmt.__scr is None:
            raise Exception("Fmt.__scr não foi inicializado")
        return Fmt.__scr.getch()

    @staticmethod
    def erase():
        if Fmt.__scr is None:
            raise Exception("Fmt.__scr não foi inicializado")
        Fmt.__scr.erase()

    @staticmethod
    def refresh():
        if Fmt.__scr is None:
            raise Exception("Fmt.__scr não foi inicializado")
        Fmt.__scr.refresh()

    @staticmethod
    def get_size():
        if Fmt.__scr is None:
            raise Exception("Fmt.__scr não foi inicializado")
        return Fmt.__scr.getmaxyx()
        

