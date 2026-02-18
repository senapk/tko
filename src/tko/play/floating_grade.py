from tko.game.task import Task
from tko.play.floating import FloatingABC, Floating
from tko.util.text import Text
from tko.game.task_grader import TaskGrader
from tko.util.symbols import symbols

# import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Callable

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
        self.index: int = index
        self.focus: bool = False

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
        if key == curses.KEY_BACKSPACE:
            if len(self.text) > 0:
                self.text = self.text[:-1]
        elif 32 <= key <= 126:
            if self.number_only:
                if chr(key).isdigit():
                    self.text += chr(key)
            else:
                info = chr(key)
                if info == "," or info == " " or info == ".":
                    self.text += info
                elif chr(key).isalpha() or chr(key).isdigit() or chr(key) == "_":
                    self.text += info

    def set_focus(self, focus: bool) -> None:
        self.focus = focus

    def set_number_only(self, number_only: bool):
        self.number_only = number_only
        return self

    def get_text(self) -> Text:
        data = Text().addf("Y" if self.focus else "", self.prompt).add(" ")
        data = data.add("├ ").addf("g",self.text).add(symbols.cursor if self.focus else "")
        return data
    
class InputBoolean(InputLine):
    def __init__(self, prefix: Text, start_value: str):
        self.prefix = prefix
        self.value = start_value
        self.focus = False

    def send_key(self, key: int) -> None:
        if key == curses.KEY_LEFT:
            self.value = "0"
            self.focus = False
        elif key == curses.KEY_RIGHT:
            self.value = "1"
            self.focus = False

    def set_focus(self, focus: bool) -> None:
        self.focus = focus
        if focus and self.value == "":
            self.value = "0"

    def get_text(self) -> Text:
        color = "Y" if self.focus else ""
        text = Text().addf(color, self.prefix).add(" │ ")
        text.addf("Y" if self.value == "0" else "", "Não").add(" ").addf("Y" if self.value == "1" else "", "Sim")
        return text


class FloatingGrade(FloatingABC):
    def __init__(self, task: Task, _align: str =""):
        self.floating = Floating(_align)
        self._task = task
        self._grader = TaskGrader(task.info)
        self._line = 0 if not task.is_leet() else 1
        self.floating.set_text_ljust()
        self.floating.frame.set_border_color("g")
        self.floating.set_header_text(Text.format("{y/}", " Utilize os direcionais e texto para marcar"))
        self.floating.set_footer_text(Text.format("{y/}", " Pressione Enter para confirmar, Esc para cancelar"))

        progression: list[tuple[str, Text]] = [
            ("x", Text().addf("g", " Nada")),
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


        if self._task.is_leet():
            texto_leet = "Testes que passaram na última execução: "
        else:
            texto_leet = "Qual percentual da atividade você fez?  "
        
        guided = "" if not self._task.info.feedback else ("1" if self._task.info.guided else "0")
        concept = "" if not self._task.info.feedback else ("1" if self._task.info.ia_concept else "0")
        problem = "" if not self._task.info.feedback else ("1" if self._task.info.ia_problem else "0")
        code = "" if not self._task.info.feedback else ("1" if self._task.info.ia_code else "0")
        debug = "" if not self._task.info.feedback else ("1" if self._task.info.ia_debug else "0")
        refactor = "" if not self._task.info.feedback else ("1" if self._task.info.ia_refactor else "0")
        
        self.rate_slide     = InputSlide(Text().add(texto_leet), progression, self._task.info.rate // 10)
        self.human_text     =     InputText(Text().add("Usou ajuda de monitor, amigo? Se sim, qual nome?    "), self._task.info.friend)
        self.time_text      =     InputText(Text().add("Tempo total estimado, estudo + código, em minutos?  "), str(self._task.info.study)).set_number_only(True)
        self.guide_text     =  InputBoolean(Text().add("Fez seguindo a aula presencial ou vídeo aula?       "), guided)
        self.iaconcept_text =  InputBoolean(Text().add("ESTUDAR conceitos sem gerar a solução do problema?  "), concept)
        self.iaproblem_text =  InputBoolean(Text().add("ENTENDER o problema a ser resolvido?                "), problem)
        self.iacode_text    =  InputBoolean(Text().add("GERAR ou CORRIGIR código relacionado ao problema?   "), code)
        self.iadebug_text   =  InputBoolean(Text().add("COMPREENDER mensagens de ERRO ou SAÍDA incorreta?   "), debug)
        self.iarefactor_text=  InputBoolean(Text().add("REFATORAR o código só após fazer tudo sozinho?      "), refactor)
        self.input_lines: list[InputLine] = [
            self.rate_slide, 
            self.human_text, 
            self.time_text,
            self.guide_text, 
            self.iaconcept_text, 
            self.iaproblem_text, 
            self.iacode_text, 
            self.iadebug_text,
            self.iarefactor_text
        ]

    def set_focus(self):
        for i, line in enumerate(self.input_lines):
            line.set_focus(i == self._line)

    def set_exit_fn(self, fn: Callable[[], None]):
        self.floating.exit_fn = fn
        return self

    def is_enable(self) -> bool:
        return self.floating.enable

    def update_content(self):
        self.set_focus()

        content = self.floating.content
        content.clear()
        content.append(Text().add("         Pontue de acordo com a última fez que você (re)fez a tarefa do zero (sprint)         "))
        width = 90
        somatorio = (Text() .addf('g', f'{round(self._task.get_percent()):>3}%'))

        content.append(Text().add("╔") + Text().add(" Tarefa:").add(somatorio).center(width, Text.Token("═", "")))
        enabled_option = "╠═ "
        op_prefix = enabled_option if not self._task.is_leet() else "║  "
        content.append(Text().add(op_prefix).add(self.rate_slide.get_text()))
        content.append(Text().add(enabled_option).add(self.human_text.get_text()))
        content.append(Text().add(enabled_option).add(self.time_text.get_text()))
        content.append(Text().add(enabled_option).add(self.guide_text.get_text()))
        content.append(Text().add("╠═") + Text().add(" Você usou IA (LLMs) para ").center(width, Text.Token("═", "")))
        content.append(Text().add(enabled_option).add(self.iaconcept_text.get_text()))
        content.append(Text().add(enabled_option).add(self.iaproblem_text.get_text()))
        content.append(Text().add(enabled_option).add(self.iacode_text.get_text()))
        content.append(Text().add(enabled_option).add(self.iadebug_text.get_text()))
        content.append(Text().add(enabled_option).add(self.iarefactor_text.get_text()))
        content.append(Text().add("╚═══════════════════════════════════════════════════════════").ljust(width, Text.Token("═", "")))


    def draw(self):
        # self.floating.set_default_header()
        # self.floating.set_default_footer()
        # self.floating.setup_frame()
        # self.floating.frame.draw()
        self.update_content()
        # self.floating.write_content()
        self.floating.draw()

    def change_task(self):
        if not self._task.is_leet():
            self._task.info.rate = self.rate_slide.index * 10
        self._task.info.feedback = True
        self._task.info.friend = self.human_text.text
        self._task.info.guided = self.guide_text.value == "1"
        self._task.info.ia_concept = self.iaconcept_text.value == "1"
        self._task.info.ia_code = self.iacode_text.value == "1"
        self._task.info.ia_debug = self.iadebug_text.value == "1"
        self._task.info.ia_problem = self.iaproblem_text.value == "1"
        self._task.info.ia_refactor = self.iarefactor_text.value == "1"
        self._task.info.set_study(self.time_text.text)

    def send_key_up(self):
        if not(self._task.is_leet() and self._line == 1):
            self._line = max(self._line - 1, 0)

    def send_key_down(self):
        self._line = min(self._line + 1, len(self.input_lines) - 1)

    def send_key(self, key: int):
        self.input_lines[self._line].send_key(key)
        self.change_task()
    
    def process_input(self, key: int) -> int:

        if key == curses.KEY_UP:
            self.send_key_up()
        elif key == curses.KEY_DOWN or key == ord("\t"):
            self.send_key_down()
        elif key == ord('\n'):
            if self._line != len(self.input_lines) - 1:
                self.send_key_down()
            else:
                self.floating.enable = False
                if self.floating.exit_fn is not None:
                    self.floating.exit_fn()
        elif key == curses.KEY_EXIT:
            self.floating.enable = False
        else:
            self.send_key(key)
        return -1