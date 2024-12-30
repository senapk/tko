from typing import List
from .frame import Frame
from ..util.text import Text, Token
from .fmt import Fmt
import curses
from typing import Callable
from rota.play.input_manager import InputManager
from rota.util.symbols import symbols
from rota.game.task import Task

class Floating:
    def __init__(self, _align=""):
        self._frame = Frame(0, 0)
        self._content: List[Text] = []
        self._type = "warning"
        self._enable = True
        self._extra_exit: List[int] = []
        self._exit_fn = None
        self._exit_key = None
        self._centralize = True
        self._floating_align = _align

    def disable(self):
        self._enable = False

    def set_text_ljust(self):
        self._centralize = False
        return self

    def set_text_center(self):
        self._centralize = True
        return self

    def set_frame_align(self, _align: str):
        self._floating_align = _align
        return self

    def set_header(self, text: str):
        self._frame.set_header(Text().addf("/", text), "")
        return self
    
    def set_header_text(self, sentence: Text):
        self._frame.set_header(sentence, "")
        return self
    
    def set_footer(self, text: str):
        self._frame.set_footer(Text().addf("/", text), "")
        return self
    
    def set_footer_text(self, sentence: Text):
        self._frame.set_footer(sentence, "")
        return self
    
    def set_exit_key(self, key: str):
        self._exit_key = ord(key)
        return self

    def set_exit_fn(self, fn):
        self._exit_fn = fn
        return self

    def _set_xy(self, dy, dx):
        valid = "<>^v"
        for c in self._floating_align:
            if c not in valid:
                raise ValueError("Invalid align " + c)

        lines, cols = Fmt.get_size()

        x = (cols - dx) // 2
        if "<" in self._floating_align:
            x = 1
        elif ">" in self._floating_align:
            x = cols - dx - 3

        y = (lines - dy) // 2
        if "^" in self._floating_align:
            y = 1
        elif "v" in self._floating_align:
            y = lines - dy - 5

        self._frame.set_pos(y, x)
        return self
            
    def is_enable(self):
        return self._enable

    def calc_dy_dx(self):
        header_len = self._frame.get_header().len()
        footer_len = self._frame.get_footer().len()
        data = [x.len() for x in self._content] + [header_len, footer_len]
        max_dx = max(data)
        dx = max_dx
        dy = len(self._content)
        return dy, dx

    def setup_frame(self):
        dy, dx = self.calc_dy_dx()
        self._frame.set_inner(dy, dx)
        self._set_xy(dy, dx)
        self._frame.set_fill()

    def put_text(self, text: str):
        lines = text.splitlines()
        for line in lines:
            self._content.append(Text().add(line))
        return self

    def put_sentence(self, sentence: Text):
        for line in sentence.split('\n'):
            self._content.append(line)
        return self
    
    def set_content(self, content: List[str]):
        self._content = [Text().add(x) for x in content]
        return self

    def _set_default_footer(self):
        if self._frame.get_footer().len() == 0:
            label = Text().addf("/", " Pressione espaço ")
            self._frame.set_footer(label, "", "─", "─")
        return self

    def _set_default_header(self):
        if self._frame.get_header().len() == 0:
            if self._type == "warning":
                self.set_header(" Aviso ")
            elif self._type == "error":
                self.set_header(" Erro ")

    def warning(self):
        self._type = "warning"
        self._frame.set_border_color("y")
        return self
    
    def error(self):
        self._type = "error"
        self._frame.set_border_color("r")
        return self

    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.setup_frame()
        self._frame.draw()
        self.write_content()

    def write_content(self):
        y = 0
        for line in self._content:
            x = 0
            if self._centralize:
                x = (self._frame.get_dx() - line.len()) // 2
            self._frame.write(y, x, line)
            y += 1
        return self

    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        key = InputManager.fix_cedilha(Fmt.get_screen(), key)
        if self._type == "warning" or self._type == "error":
            if key < 300:
                self._enable = False
                if self._exit_fn is not None:
                    self._exit_fn()
                if self._exit_key is not None:
                    return self._exit_key
                if key == ord(" ") or key == 27:
                    return -1
                return key
        
        return -1
        
class FloatingGrade(Floating):
    def __init__(self, task: Task, _align=""):
        super().__init__(_align)
        self._task = task
        self._line = 0
        self.set_text_ljust()
        self._frame.set_border_color("g")
        self.set_header_text(Text.format("{y/}", " Utilize os direcionais para  marcar "))
        self.set_footer_text(Text.format("{y/}", " Pressione Enter para confirmar "))

        self.grades_index = [task.coverage // 10, task.autonomy, task.ability]
        self.coverage = ["x", "1", "2", "3", "4", "5", "6", "7", "8", "9", "✓"]
        self.coverage_msg = [
            "Não fiz", 
            "Fiz 10%", 
            "Fiz 20%", 
            "Fiz 30%", 
            "Fiz 40%",
            "Fiz 50%",
            "Fiz 60%",
            "Fiz 70%",
            "Fiz 80%",
            "Fiz 90%",
            "Fiz 100%"]
        self.autonomy = [x.text for x in [symbols.autonomy_x, symbols.autonomy_e, symbols.autonomy_d, symbols.autonomy_c, symbols.autonomy_b, symbols.autonomy_a]]
        self.autonomy_msg = [
            "Não fiz             ", 
            "Copiei              ", 
            "Fiz guiado          ", 
            "Fiz com muita ajuda ", 
            "Fiz com ajuda       ", 
            "Fiz sem ajuda       "
            ]
        self.hability = [x.text for x in [symbols.hability_x, symbols.hability_e, symbols.hability_d, symbols.hability_c, symbols.hability_b, symbols.hability_a]]
        self.hability_msg = [
            "Não fiz            ", 
            "Não entendi        ", 
            "Entendi uma parte  ", 
            "Entendi boa parte  ", 
            "Entendi quase tudo ", 
            "Entendi tudo       "
            ]
        self.grades_value = [self.coverage, self.autonomy, self.hability]
        self.grades_msg = [self.coverage_msg, self.autonomy_msg, self.hability_msg]

    
    def update_content(self):
        self._content = []
        self._content.append(Text())
        coverage_text = Text().add("   ").addf("Y" if self._line == 0 else "", "Cobertura").add("  ")
        for i, c in enumerate(self.coverage):
            coverage_text.addf("C" if i == self.grades_index[0] else "", c)
        coverage_text.add("  ").addf("m", self.coverage_msg[self.grades_index[0]])
        self._content.append(coverage_text)
        # self._content.append(Text())
        hability_text = Text().add("   ").addf("Y" if self._line == 1 else "", "Autonomia").add("  ")
        for i, c in enumerate(self.autonomy):
            hability_text.addf("G" if i == self.grades_index[1] else "", c).add(" ")
        hability_text.add(" ").addf("m", self.autonomy_msg[self.grades_index[1]])
        self._content.append(hability_text)
        # self._content.append(Text())
        autonomy_text = Text().add(" ").addf("Y" if self._line == 2 else "", "Compreensão").add("  ")
        for i, c in enumerate(self.hability):
            autonomy_text.addf("yW" if i == self.grades_index[2] else "", c).add(" ")
        autonomy_text.add(" ").addf("m", self.hability_msg[self.grades_index[2]])
        self._content.append(autonomy_text)
        self._content.append(Text())
        
    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.setup_frame()
        self._frame.draw()
        self.update_content()
        self.write_content()

    def change_task(self):
        self._task.set_coverage(self.grades_index[0] * 10)
        self._task.set_autonomy(self.grades_index[1])
        self._task.set_hability(self.grades_index[2])

    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        key = InputManager.fix_cedilha(Fmt.get_screen(), key)
        if key == curses.KEY_UP or key == ord('w'):
            self._line = max(self._line - 1, 0)
        elif key == curses.KEY_DOWN or key == ord('s'):
            self._line = min(self._line + 1, 2)
        elif key == curses.KEY_LEFT or key == ord('a'):
            self.grades_index[self._line] = max(self.grades_index[self._line] - 1, 0)
            self.change_task()
        elif key == curses.KEY_RIGHT or key == ord('d'):
            self.grades_index[self._line] = min(self.grades_index[self._line] + 1, len(self.grades_value[self._line]) - 1)
            self.change_task()
        elif key == ord('\n') or key == curses.KEY_BACKSPACE or key == InputManager.esc:
            self._enable = False
            if self._exit_fn is not None:
                self._exit_fn()        
        return -1

class FloatingInputData:
    def __init__(self, label: Callable[[], Text], action: Callable[[], None], shortcut: str = ""):
        self.label = label
        self.action = action
        self.shortcut = shortcut
        self.exit_on_action = False


    def set_exit_on_action(self, value: bool):
        self.exit_on_action = value
        return self

class FloatingInput(Floating):
    def __init__(self, _align=""):
        super().__init__(_align)
        self._index = 0
        self._options: List[FloatingInputData] = []
        self._frame.set_border_color("m")
        self._exit_on_action = True
        self.right_dx = 5 # shortcut space
        self.search_text: List[str] = []

    def calc_dy_dx(self):
        dy, dx = super().calc_dy_dx()
        dy += len(self._options) + 2
        for option in self._options:
            dx = max(dx, len(option.label()))
        return dy, dx + self.right_dx
    
    def set_exit_on_enter(self, value: bool):
        self._exit_on_action = value
        return self

    def match_search(self, index: int):
        return "".join(self.search_text) in self._options[index].label().get_text().lower()

    def next_option(self):
        if not self.match_search(self._index):
            self._index = 0
        steps = len(self._options)
        index = self._index
        while steps > 0:
            index = (index + 1) % len(self._options)
            if self.match_search(index):
                self._index = index
                return
            steps -= 1
    
    def prev_option(self):
        if not self.match_search(self._index):
            self._index = 0
        steps = len(self._options)
        index = self._index
        while steps > 0:
            index = (index - 1) % len(self._options)
            if self.match_search(index):
                self._index = index
                return
            steps -= 1

    def write_content(self):
        options: List[Text] = []
        dx = self._frame.get_dx() - self.right_dx
        for i, option in enumerate(self._options):
            if not self.match_search(i):
                continue
            text = Text().add(option.label()).ljust(dx)
            if option.shortcut != "":
                if len(option.shortcut) > 1:
                    text.add(" " + option.shortcut)
                else:
                    text.add(f" [{option.shortcut}]")
            fmt = "M" if i == self._index else ""
            text.set_background(fmt)
            options.append(text)
        
        self._frame.write(0, 0, Text.format("Busca: ") + "".join(self.search_text) + symbols.cursor)
        y = 1
        for line in self._content + options:
            x = 0
            if self._centralize:
                x = (self._frame.get_dx() - line.len()) // 2
            self._frame.write(y, x, line)
            y += 1

        return self

    def set_options(self, options: List[FloatingInputData]):
        self._options = options
        return self
    
    def set_default_index(self, index: int):
        self._index = index
        return self

    def update_index(self):
        for i, _ in enumerate(self._options):
            if self.match_search(i):
                self._index = i
                return
        self._index = -1

    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        key = InputManager.fix_cedilha(Fmt.get_screen(), key)
        
        if key == curses.KEY_UP:
            self.prev_option()
        elif key == curses.KEY_DOWN:
            self.next_option()
        elif key == InputManager.esc:
            self._enable = False
        elif any([key == x for x in InputManager.backspace_list]) or key == InputManager.delete:
            self.search_text = self.search_text[:-1]
            self.update_index()
        elif key >= 32 and key < 127:
            self.search_text += chr(key).lower()
            self.update_index()
        elif key == ord('\n'):
            if self._exit_on_action or self._options[self._index].exit_on_action:
                self._enable = False
            if self._index != -1:
                self._options[self._index].action()
            return -1
        else:
            return key
        return -1
