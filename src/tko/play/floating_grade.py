from tko.game.task import Task
from tko.play.floating import Floating
from tko.play.input_manager import InputManager
from tko.util.text import Text
from tko.settings.settings import Settings
from tko.game.task_grader import TaskGrader
from tko.util.symbols import symbols

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
        color = "Y" if self.focus else ""
        text = Text().addf(color, self.prefix).add(" ")
        for i, c in enumerate(self.opt_msgs):
            opt, _ = c
            text.addf("Y" if i == self.index else "", opt)
        text.add(" ├").add(self.opt_msgs[self.index][1])
        return text
    
class InputText(InputLine):
    def __init__(self, prompt: Text, text: str = ""):
        self.prompt = prompt
        self.text = text
        self.focus = False
        self.number_only = False

    def send_key(self, key: int) -> None:
        if key in InputManager.backspace_list:
            if len(self.text) > 0:
                self.text = self.text[:-1]
        elif 32 <= key <= 126:
            if self.number_only:
                if chr(key).isdigit():
                    self.text += chr(key)
            else:
                info = chr(key)
                if info == "," or info == " " or info == ".":
                    info = "_"
                    self.text += info
                elif chr(key).isalpha() or chr(key).isdigit() or chr(key) == "_":
                    self.text += info

    def set_focus(self, focus: bool) -> None:
        self.focus = focus

    def set_number_only(self, number_only: bool):
        self.number_only = number_only
        return self

    def get_text(self) -> Text:
        data = Text().addf("Y" if self.focus else "", self.prompt).add("   ")
        if not self.number_only:
            data = data.addf("Y" if len(self.text) == 0 else "", "NÃO").add(" ").addf("Y" if len(self.text) > 0 else "", "SIM").add("   ")
        data = data.add("├ ").addf("g",self.text).add(symbols.cursor if self.focus else "")
        return data


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

        self.rate_slide  = InputSlide(Text().add("Quanto alcançou nessa sprint        ?"), progression, self._task.info.rate // 10)
        self.alone_slide = InputSlide(Text().add("Quanto fez só, por tentativa e erro ?"), progression, self._task.info.alone)
        self.human_text  =  InputText(Text().add("Ajuda Humana   (monitor, amigo, ...)?"), self._task.info.human)
        self.iagen_text  =  InputText(Text().add("Ajuda IA         (copilot, gpt, ...)?"), self._task.info.iagen)
        self.guide_text  =  InputText(Text().add("Ajuda Guiada      (aula, vídeo, ...)?"), self._task.info.guide)
        self.other_text  =  InputText(Text().add("Ajuda Outros     (livro, fórum, ...)?"), self._task.info.other)
        self.time_text   =  InputText(Text().add("Tempo total estimado (estudo + código) minutos:"), str(self._task.info.study)).set_number_only(True)
        self.input_lines: list[InputLine] = [self.rate_slide, self.alone_slide, self.human_text, self.iagen_text, self.guide_text, self.other_text, self.time_text]

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


    def set_focus(self):
        for i, line in enumerate(self.input_lines):
            line.set_focus(i == self._line)

    def update_content(self):
        self.set_focus()
        self._content = []
        self._content.append(Text().add("         Pontue de acordo com a última fez que você (re)fez a tarefa do zero (sprint)         "))
        width = 90
        somatorio = (Text() .addf('g', f'{round(self._task.get_percent()):>3}%'))

        self._content.append(Text().add("╔") + Text().add(" Tarefa:").add(somatorio).add(" ══╤").center(width, Text.Token("═", "")))
        enabled_option = "╠═ "
        op_prefix = enabled_option if not self._task.is_leet() else "║  "
        self._content.append(Text().add(op_prefix).add(self.rate_slide.get_text()))
        self._content.append(Text().add(enabled_option).add(self.alone_slide.get_text()))
        self._content.append(Text().add(enabled_option).add(self.human_text.get_text()))
        self._content.append(Text().add(enabled_option).add(self.iagen_text.get_text()))
        self._content.append(Text().add(enabled_option).add(self.guide_text.get_text()))
        self._content.append(Text().add(enabled_option).add(self.other_text.get_text()))
        self._content.append(Text().add("╠═ ").add(self.time_text.get_text()))
        self._content.append(Text().add("╚════════════════════════════════════════════════════╧═").ljust(width, Text.Token("═", "")))


    # @override
    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.setup_frame()
        self._frame.draw()
        self.update_content()
        self.write_content()

    def change_task(self):
        if not self._task.is_leet():
            self._task.info.rate = self.rate_slide.index * 10
        self._task.info.set_alone(self.alone_slide.index)
        self._task.info.set_human(self.human_text.text)
        self._task.info.set_iagen(self.iagen_text.text)
        self._task.info.set_guide(self.guide_text.text)
        self._task.info.set_other(self.other_text.text)
        try:
            self._task.info.study = int(self.time_text.text)
        except:
            self._task.info.study = 0

    def send_key_up(self):
        if not(self._task.is_leet() and self._line == 1):
            self._line = max(self._line - 1, 0)

    def send_key_down(self):
        self._line = min(self._line + 1, len(self.input_lines) - 1)

    def send_key(self, key: int):
        self.input_lines[self._line].send_key(key)
        self.change_task()

    
    # @override
    def process_input(self, key: int) -> int:

        if key == curses.KEY_UP:
            self.send_key_up()
        elif key == curses.KEY_DOWN or key == ord("\t"):
            self.send_key_down()
        elif key == ord("+") or key == ord("="):
            self.send_key(key)
            self.send_key_down()
        elif key == ord("-"):
            self.send_key(key)
            self.send_key_up()
        elif key == ord('\n'):
            if self._line != len(self.input_lines) - 1:
                self.send_key_down()
            else:
                self._enable = False
                if self._exit_fn is not None:
                    self._exit_fn()
        elif key == InputManager.esc:
            self._enable = False
            if self._exit_fn is not None:
                self._exit_fn()
        else:
            self.send_key(key)
        return -1