import curses
from typing import Dict, List, Tuple
from ..game.sentence import Sentence
from .style import Style

class Fmt:
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
    def __write_line(stdscr, y: int, x: int, fmt: str, text: str):
        italic = False
        underline = False

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
                print("Cor não encontrada: " + fg + bg)
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
        except curses.error as e:
            print(str(e))
            print(f"y:{y}, x:{x}, fmt:{fmt}, text: {text}")
        if pair_number != -1:
            stdscr.attroff(curses.color_pair(pair_number))
        if italic:
            stdscr.attroff(curses.A_ITALIC)
        if underline:
            stdscr.attroff(curses.A_UNDERLINE)

    @staticmethod
    def write(stdscr, y: int, x: int, sentence: Sentence):
        # Escreve um texto na tela com cores diferentes
        lines, cols = stdscr.getmaxyx()
        for fmt, text in sentence.get():
            if x < cols and y < lines:
                if x + len(text) >= cols:
                    text = text[:cols - x - 1]
                Fmt.__write_line(stdscr, y, x, fmt, text)
            x += len(text)  # Move a posição x para a direita após o texto

    @staticmethod
    def get_user_input(stdscr, prompt: str) -> str:
        lines, cols = stdscr.getmaxyx()
        curses.echo()  # Ativa a exibição dos caracteres digitados
        curses.curs_set(1)  # Ativa o cursor
        stdscr.addstr(0, 0, cols * " ")
        stdscr.addstr(0, 0, prompt)
        stdscr.refresh()
        input_str = stdscr.getstr(0, len(prompt), 20).decode('utf-8')  # Captura o input do usuário
        curses.noecho()  # Desativa a exibição dos caracteres digitados
        curses.curs_set(0)
        return input_str

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