from tko.play.floating import Floating, FloatingABC
from tko.util.symbols import symbols
from tko.util.text import Text
from typing import Callable

import curses

class FloatingInputData:
    def __init__(self, label: Callable[[], Text], action: Callable[[], None], shortcut: str = ""):
        self.label = label
        self.action = action
        self.shortcut = shortcut
        self.exit_on_action = False

    def set_exit_on_action(self, value: bool):
        self.exit_on_action = value
        return self


class FloatingDropDown(FloatingABC):
    def __init__(self):
        self.floating = Floating()
        self.index = 0
        self.options: list[FloatingInputData] = []
        self.floating.frame.set_border_color("m")
        self.exit_on_action = True
        self.right_dx = 5 # shortcut space
        self.search_text: list[str] = []

    def set_floating(self, floating: Floating):
        self.floating = floating
        return self

    # @override
    def is_enable(self) -> bool:
        return self.floating.is_enable()
    
    # @override
    def draw(self):
        self.floating.draw()
        self.write_content()

    def calc_dy_dx(self):
        dy, dx = self.floating.calc_dy_dx()
        dy += len(self.options) + 2
        for option in self.options:
            dx = max(dx, len(option.label()))
        return dy, dx + self.right_dx

    def set_exit_on_enter(self, value: bool):
        self.exit_on_action = value
        return self

    def match_search(self, index: int):
        return "".join(self.search_text) in self.options[index].label().get_str().lower()

    def next_option(self):
        if not self.match_search(self.index):
            self.index = 0
        steps = len(self.options)
        index = self.index
        while steps > 0:
            index = (index + 1) % len(self.options)
            if self.match_search(index):
                self.index = index
                return
            steps -= 1

    def prev_option(self):
        if not self.match_search(self.index):
            self.index = 0
        steps = len(self.options)
        index = self.index
        while steps > 0:
            index = (index - 1) % len(self.options)
            if self.match_search(index):
                self.index = index
                return
            steps -= 1

    def write_content(self):
        options: list[Text] = []
        dx = self.floating.frame.get_dx() - self.right_dx
        for i, option in enumerate(self.options):
            if not self.match_search(i):
                continue
            text = Text().add(option.label()).ljust(dx)
            if option.shortcut != "":
                if len(option.shortcut) > 1:
                    text.add(" " + option.shortcut)
                else:
                    text.add(f" [{option.shortcut}]")
            fmt = "M" if i == self.index else ""
            text.set_background(fmt)
            options.append(text)

        self.floating.frame.write(0, 0, Text.format("Busca: ") + "".join(self.search_text) + symbols.cursor)
        y = 1
        for line in self.floating.content + options:
            x = 0
            if self.floating.centralize_text:
                x = (self.floating.frame.get_dx() - line.len()) // 2
            self.floating.frame.write(y, x, line)
            y += 1

        return self

    def set_options(self, options: list[FloatingInputData]):
        self.options = options
        return self

    def set_default_index(self, index: int):
        self.index = index
        return self

    def update_index(self):
        for i, _ in enumerate(self.options):
            if self.match_search(i):
                self.index = i
                return
        self.index = -1

    # @override
    def process_input(self, key: int) -> int:
        # self.draw()

        if key == curses.KEY_UP:
            self.prev_option()
        elif key == curses.KEY_DOWN:
            self.next_option()
        elif key == curses.KEY_LEFT:
            self.search_text = self.search_text[:-1]
            self.update_index()
        elif 32 <= key < 127:
            self.search_text += chr(key).lower()
            self.update_index()
        elif key == curses.KEY_BACKSPACE:
            if len(self.search_text) > 0:
                self.search_text = self.search_text[:-1]
            else:
                self.search_text = []
            self.update_index()
        elif key == ord('\n'):
            if self.exit_on_action or self.options[self.index].exit_on_action:
                self.floating.enable = False
            if self.index != -1:
                self.options[self.index].action()
            return -1
        elif key == curses.KEY_EXIT:
            self.floating.enable = False
            if self.floating.exit_fn is not None:
                self.floating.exit_fn()
            return -1
        else:
            return key
        return -1