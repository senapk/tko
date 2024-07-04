from typing import List, Tuple
from .frame import Frame
from ..util.sentence import Sentence
from .fmt import Fmt

import curses
import time

class Input:
    def __init__(self):
        self.frame = Frame(0, 0)
        self.content: List[Sentence] = []
        self.ending = None
        self.total_time = None
        self.type = ""
        self.options = []
        self.options_index = 0
        self.fn_answer = None
        self.enable = True
        self.extra_exit: List[int] = []
        self.exit_fn = None
        self.exit_key = None
        self._centralize = True

    def set_header(self, text: Sentence, align: str = '<'):
        self.frame.set_header(text, align)
        return self
    
    def set_exit_key(self, key: str):
        self.exit_key = ord(key)
        return self

    def set_exit_fn(self, fn):
        self.exit_fn = fn
        return self

    def add_extra_exit(self, key: str):
        self.extra_exit.append(ord(key[0]))
        return self

    def __setup_frame(self):
        lines, cols = Fmt.get_size()
        max_dx = max([x.len() for x in self.content])
        dx = max_dx + 2
        dy = len(self.content) + 2
        x = (cols - dx) // 2
        y = (lines - dy) // 2
        self.frame.set_pos(y, x).set_inner(dy, dx)
        self.frame.set_fill()
        # if self.type == "timer":
        #     delta = dx - 4
        #     percent = (self.ending - time.time()) / self.total_time
        #     footer = (delta - int(delta * percent)) * "─" + int(delta * percent) * "━"
        #     self.frame.set_footer(Sentence().addt(footer), "^")
        
        if self.type == "answer":
            footer = Sentence().addt(" ")
            for i, option in enumerate(self.options):
                fmt = "kG" if i == self.options_index else ""
                footer.addf(fmt, option).addt(" ")
            self.frame.set_footer(footer, "^")

    def ljust(self):
        self._centralize = False

    def addt(self, text: str):
        self.content.append(Sentence().addt(text))
        return self

    def adds(self, sentence: Sentence):
        self.content.append(sentence)
        return self
    
    def set_content(self, content: List[str]):
        self.content = [Sentence().addt(x) for x in content]
        return self

    def timer(self, delta: int):
        self.total_time = delta
        self.ending = time.time() + delta
        return self

    def warning(self):
        self.type = "warning"
        if self.frame.get_header().len() == 0:
            self.frame.set_header(Sentence().addf("/", " Aviso "))
        self.frame.set_footer(Sentence().addf("/", " Pressione enter "))
        self.frame.set_border_color("y")
        return self
    
    def error(self):
        self.type = "warning"
        if self.frame.get_header().len() == 0:
            self.frame.set_header(Sentence().addf("/", " Erro "))
        self.frame.set_footer(Sentence().addf("/", " Pressione enter "))
        self.frame.set_border_color("r")
        return self
    
    def set_options(self, options: List[str]):
        self.options = options
        return self
    
    def get_answer(self, fn_answer):
        self.type = "answer"
        self.frame.set_border_rounded()
        self.frame.set_header(Sentence().addf("/", " Pergunta "))
        # self.frame.set_footer(Sentence().addf("/", " Selecione e aperte enter "))
        self.fn_answer = fn_answer
        return self

    def draw(self):
        self.__setup_frame()
        self.frame.draw()
        for i, line in enumerate(self.content):
            if self._centralize:
                x = (self.frame.get_dx() - line.len()) // 2
                self.frame.write(i + 1, x, line)
            else:
                self.frame.write(i + 1, 1, line)
        return self

    def timer_expired(self):
        if self.ending is None:
            return False
        return time.time() > self.ending

    def get_input(self) -> int:
        self.draw()
        key = Fmt.getch()
        if self.type == "warning" or self.type == "answer":
            if key == ord('\n') or key == 27 or key in self.extra_exit or self.timer_expired():
                self.enable = False
                if self.exit_fn is not None:
                    self.exit_fn()
                if self.exit_key is not None:
                    return self.exit_key
        if self.type == "answer":
            if key == curses.KEY_LEFT:
                self.options_index = (self.options_index - 1) % len(self.options)
            elif key == curses.KEY_RIGHT:
                self.options_index = (self.options_index + 1) % len(self.options)
            elif key == ord('\n'):
                self.enable = False
                if self.fn_answer is not None:
                    self.fn_answer(self.options[self.options_index])
                if self.exit_fn is not None:
                    self.exit_fn()
                if self.exit_key is not None:
                    return self.exit_key
                return -1
        return -1
        