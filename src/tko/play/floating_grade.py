from tko.game.task import Task
from tko.play.floating import Floating
from tko.play.fmt import Fmt
from tko.play.input_manager import InputManager
from tko.util.text import Text
from tko.play.keys import GuiKeys
from tko.settings.settings import Settings
from tko.game.task_grader import TaskGrader

# import ABC, abstractmethod
from abc import ABC, abstractmethod

# from typing import override

import curses


class InputLine(ABC):

    @abstractmethod
    def send_key(self, key: int) -> None:
        pass

    @abstractmethod
    def set_focus(self, focus: bool) -> None:
        pass

    @abstractmethod
    def get_text(self) -> Text:
        pass

class InputSlide(InputLine):
    def __init__(self, prefix: Text, opt_msgs: list[tuple[str, Text]], index: int = 0):
        self.prefix = prefix
        self.opt_msgs = opt_msgs
        self.index = index
        self.focus = False

    def send_key(self, key: int) -> None:
        size = len(self.opt_msgs)
        if key == curses.KEY_LEFT:
            self.index = max(0, self.index - 1)
        elif key == curses.KEY_RIGHT:
            self.index = min(size - 1, self.index + 1)
        elif key == ord("-"):
            self.index = 0
        elif key == ord("+") or key == ord("="):
            self.index = size - 1

    def set_focus(self, focus: bool) -> None:
        self.focus = focus

    def get_text(self) -> Text:
        text = Text().add(self.prefix)
        color = "C" if self.focus else "Y"
        for i, c in enumerate(self.opt_msgs):
            opt, _ = c
            text.addf(color if i == self.index else "", opt)
        text.add(self.opt_msgs[self.index][1])
        return text


class FloatingGrade(Floating):
    def __init__(self, task: Task, settings: Settings, _align: str =""):
        super().__init__(settings, _align)
        self.settings = settings
        self._task = task
        self._grader = TaskGrader(task.info)
        self._line = 0 if not task.is_leet() else 1
        self.set_text_ljust()
        self._frame.set_border_color("g")
        self.set_header_text(Text.format("{y/}", " Utilize os direcionais, texto, tab e +/- para marcar"))
        self.set_footer_text(Text.format("{y/}", " Pressione Enter para confirmar "))

        progression: list[tuple[str, Text]] = [
            ("x", Text().addf("g", " Não ").addf("y", "fiz")),
            ("1", Text().addf("y", " 10%")),
            ("2", Text().addf("y", " 20%")),
            ("3", Text().addf("y", " 30%")),
            ("4", Text().addf("y", " 40%")),
            ("5", Text().addf("y", " 50%")),
            ("6", Text().addf("y", " 60%")),
            ("7", Text().addf("y", " 70%")),
            ("8", Text().addf("y", " 80%")),
            ("9", Text().addf("y", " 90%")),
            ("✓", Text().addf("y", " 100%"))]

        self.rate_slide  = InputSlide(Text().add("Quanto entregou ao final dessa sprint? "), progression, self._task.info.rate // 10)
        self.alone_slide = InputSlide(Text().add("Quanto fez antes de procurar ajuda   ? "), progression, min(self._task.info.alone // 10, 10))

        # self.questions: dict[str, str] = {}
        # rate_question  = "Quanto entregou ao final dessa sprint?"
        # alone_question = "Quanto fez antes de procurar ajuda   ?"
        # human_question = "Ajuda de alguém(monitor, amigo)      ?"
        # iagen_question = "Ajuda de IA (copilot, gpt)           ?"
        # guide_question = "Ajuda guiada (aula, vídeo)           ?"
        # other_question = "Ajuda de outras fontes               ?"
        # self.questions["rate"] = rate_question
        # self.questions["alone"] = alone_question
        # self.questions["human"] = human_question
        # self.questions["iagen"] = iagen_question
        # self.questions["guide"] = guide_question
        # self.questions["other"] = other_question



    def update_content(self):
        self._content = []
        self._content.append(Text().add("         Pontue de acordo com a última fez que você (re)fez a tarefa do zero (sprint)         "))
        width = 90
        somatorio = (Text() .addf('g', f'{round(self._task.get_percent()):>3}%'))

        self._content.append(Text().add("╔") + Text().add(" Tarefa:").add(somatorio).add(" ").center(width, Text.Token("═", "")))
        opening = "╠═ "
        op_prefix = opening if not self._task.is_leet() else "║  "
        self._content.append(Text().add(op_prefix).add(self.rate_slide.get_text()))
        self._content.append(Text().add("║  ").add(self.alone_slide.get_text()))
        self._content.append(Text().add("╚══════════════════════════════════════════════════════════════════════════════════════════"))

    # @override
    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.setup_frame()
        self._frame.draw()
        self.update_content()
        self.write_content()

    def change_task(self):
        pass # modificar a tarefa de fato

    def send_key_up(self):
        if not(self._task.is_leet() and self._line == 1):
            self._line = max(self._line - 1, 0)

    def send_key_down(self):
        self._line = min(self._line + 1, 1)

    def send_key(self, key: int):
        if self._line == 0:
            self.rate_slide.send_key(key)
        elif self._line == 1:
            self.alone_slide.send_key(key)
    
    # @override
    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        key = InputManager.fix_cedilha(Fmt.get_screen(), key)
        if key == self.settings.app.get_key_up() or key == ord(GuiKeys.up):
            self.send_key_up()
        elif key == self.settings.app.get_key_down() or key == ord(GuiKeys.down):
            self.send_key_down()
        elif key == ord("+") or key == ord("="):
            self.send_key(key)
            self.send_key_down()
        elif key == ord("-"):
            self.send_key(key)
            self.send_key_up()
        elif key == ord('\n') or key == curses.KEY_BACKSPACE or key == InputManager.esc:
            self._enable = False
            if self._exit_fn is not None:
                self._exit_fn()
        return -1