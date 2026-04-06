from __future__ import annotations
from tko.game.task import Task
from tko.play.floating import FloatingABC, Floating
from tko.util.text import Text
from tko.util.symbols import Symbols

# import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Callable

# from typing import override

import curses


class InputLine(ABC):
    SELECTED_COLOR = "y"
    LOCKED_COLOR = "r"
    OPTION_COLOR = "X"

    def __init__(self, id: str):
        self.id = id
        self.locked = False
        self.focus = False

    def get_selected_color(self) -> str:
        if self.locked:
            return self.LOCKED_COLOR
        return self.SELECTED_COLOR

    def get_opening(self):
        return Text().add(Symbols.right_triangle_filled if self.focus else " ").add(" ")

    @abstractmethod
    def send_key(self, key: int) -> None:
        pass

    def set_focus(self, focus: bool) -> InputLine:
        self.focus = focus
        return self

    @abstractmethod
    def get_text(self, pad: int) -> Text:
        pass

    @abstractmethod
    def get_value(self) -> str:
        pass

    def set_locked(self, value: bool) -> InputLine:
        self.locked = value
        return self

    def is_locked(self) -> bool:
        return self.locked

class InputSlide(InputLine):
    def __init__(self, id: str, prefix: Text, opt_msgs: list[tuple[str, Text]], index: int = 0):
        super().__init__(id)
        self.prefix = prefix
        self.opt_msgs = opt_msgs
        self.index: int = index

    def get_value(self) -> str:
        return str(self.index)

    def send_key(self, key: int) -> None:
        if self.is_locked():
            return
        size = len(self.opt_msgs)
        if key == curses.KEY_LEFT:
            self.index = max(0, self.index - 1)
        elif key == curses.KEY_RIGHT:
            self.index = min(size - 1, self.index + 1)
        elif key == ord("-"):
            self.index = 0
        elif key == ord("+") or key == ord("="):
            self.index = size - 1

    def get_text(self, pad: int) -> Text:
        color = self.get_selected_color() if self.focus else ""
        text = Text().add(self.get_opening()).addf(color, self.prefix).add(" ")
        for i, c in enumerate(self.opt_msgs):
            opt, _ = c
            text.addf(self.OPTION_COLOR if i == self.index else color, opt)
        text.ljust(pad)
        text.add(" ├").add(self.opt_msgs[self.index][1])
        return text
    
class InputText(InputLine):
    def __init__(self, id: str, prompt: Text, text: str = ""):
        super().__init__(id)
        self.prompt = prompt
        self.text = text
        self.focus = False
        self.number_only = False

    def get_value(self) -> str:
        return self.text

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

    def set_number_only(self, number_only: bool):
        self.number_only = number_only
        return self

    def get_text(self, pad: int) -> Text:
        data = Text().add(self.get_opening()).addf(self.get_selected_color() if self.focus else "", self.prompt).ljust(pad).add(" ")
        data = data.add("├ ").addf(self.OPTION_COLOR, self.text).add(Symbols.cursor if self.focus else "")
        return data
    
class InputBoolean(InputLine):
    def __init__(self, id: str, prefix: Text, start_value: str):
        super().__init__(id)
        self.prefix = prefix
        self.value = start_value

    def get_value(self) -> str:
        return self.value

    def send_key(self, key: int) -> None:
        if key == curses.KEY_LEFT:
            self.value = "0"
            self.focus = False
        elif key == curses.KEY_RIGHT:
            self.value = "1"
            self.focus = False

    def set_focus(self, focus: bool) -> InputLine:
        self.focus = focus
        if focus and self.value == "":
            self.value = "0"
        return self

    def get_text(self, pad: int) -> Text:
        color = self.get_selected_color() if self.focus else ""
        text = Text().add(self.get_opening())
        if self.focus:
            text.addf(color, self.prefix)
        else:
            text.add(self.prefix)
        text.ljust(pad).add("│ ")
        text.addf(self.OPTION_COLOR if self.value == "0" else color, "Não").add(" ").addf(self.OPTION_COLOR if self.value == "1" else color, "Sim")
        return text

class FloatingGrade(FloatingABC):
    def __init__(self, task: Task, fn_exit: Callable[[Task], None] | None = None):
        self.floating = Floating()
        self._task = task
        self._line = 0
        self.floating.set_text_ljust()
        self.floating.frame.set_border_color("g")
        self.floating.set_header_text(Text.format("{y/}", " Utilize os direcionais e texto para marcar"))
        self.floating.set_footer_text(Text.format("{y/}", " Pressione Enter para confirmar, Esc para cancelar"))
        self.fn_exit = fn_exit

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


        if self._task.is_auto():
            texto_auto = "Taxa de testes que passou na última execução:"
        else:
            texto_auto = "Informe qual percentual da atividade você fez?"
        
        guided = "" if not self._task.info.feedback else ("1" if self._task.info.guided else "0")
        concept = "" if not self._task.info.feedback else ("1" if self._task.info.ia_concept else "0")
        problem = "" if not self._task.info.feedback else ("1" if self._task.info.ia_problem else "0")
        code = "" if not self._task.info.feedback else ("1" if self._task.info.ia_code else "0")
        debug = "" if not self._task.info.feedback else ("1" if self._task.info.ia_debug else "0")
        refactor = "" if not self._task.info.feedback else ("1" if self._task.info.ia_refactor else "0")

        self.quantity_input_lines: list[InputLine] = [
            InputSlide("rate", Text().add(texto_auto), progression, self._task.info.rate // 10).set_locked(self._task.is_auto()),
            InputText("study", Text().add("Qual tempo total estimado, estudo + código, em minutos?"), str(self._task.info.study)).set_number_only(True),
        ]
        self.support_input_lines: list[InputLine] = [
            InputText("friend", Text().add("Deixe em branco se fez sozinho, ou com o nome de quem ajudou"), self._task.info.friend),
            InputBoolean("guided",  Text().add("Fez o código copiando da aula ou vídeo aula?      ").addf("g", "   COPIOU:").add(self.get_discount("guided")), guided),
        ]
        self.quality_input_lines: list[InputLine] = [
            InputBoolean("concept", Text().add("ESTUDAR conceitos sem gerar a solução do problema?").addf("g", "  ESTUDAR:").add(self.get_discount("concept")), concept),
            InputBoolean("problem", Text().add("ENTENDER o problema a ser resolvido?              ").addf("g", " ENTENDER:").add(self.get_discount("problem")), problem),
            InputBoolean("code",    Text().add("GERAR ou CORRIGIR código relacionado ao problema? ").addf("g", " CORRIGIR:").add(self.get_discount("code")), code),
            InputBoolean("debug",   Text().add("COMPREENDER mensagens de ERRO ou SAÍDA incorreta? ").addf("g", "  DEBUGAR:").add(self.get_discount("debug")), debug),
            InputBoolean("refactor",Text().add("REFATORAR o código só após fazer tudo sozinho?    ").addf("g", "REFATORAR:").add(self.get_discount("refactor")), refactor),
        ]
        self.all_input_lines: list[InputLine] = self.quantity_input_lines + self.support_input_lines + self.quality_input_lines
        self.input_dict: dict[str, InputLine] = {line.id: line for line in self.all_input_lines}

    def get_discount(self, tag: str) -> Text:
        grade_dict = self._task.grader.grades
        value = grade_dict.get(self._task.task_loss.value, {}).get(tag, 100)
        size = 5
        if value == 100:
            return Text().addf("g", " " * size)
        else:
            return Text().addf("y", f"-{100 - value}%".ljust(size))

    def set_focus(self):
        for i, line in enumerate(self.all_input_lines):
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
        pad = 66
        dummy_task = self._task.clone()
        self.change_task(dummy_task, self.input_dict)
        somatorio = (Text() .addf('g', f'{round(dummy_task.get_rate_percent() * dummy_task.get_quality_percent()/100):>3}% '))

        content.append(Text().add("╔") + Text().add(" Tarefa:").add(somatorio).center(width, Text.Token("═", "")))
        left_side = "║ "
        for line in self.quantity_input_lines:
            content.append(Text().add(left_side).add(line.get_text(pad)))
        content.append(Text().add("╠═") + Text().add(" Você fez com ajuda humana ou guiado? ").center(width, Text.Token("═", "")))
        for line in self.support_input_lines:
            content.append(Text().add(left_side).add(line.get_text(pad)))
        content.append(Text().add("╠═") + Text().add(" Você usou IA (LLMs) para ").center(width, Text.Token("═", "")))
        for line in self.quality_input_lines:
            content.append(Text().add(left_side).add(line.get_text(pad)))
        content.append(Text().add("╚═══════════════════════════════════════════════════════════").ljust(width, Text.Token("═", "")))


    def draw(self):
        self.update_content()
        self.floating.draw()

    @staticmethod
    def change_task(task: Task, input_dict: dict[str, InputLine]):
        if not task.is_auto():
            task.info.rate = int(input_dict["rate"].get_value()) * 10
        task.info.feedback = True
        task.info.friend = input_dict["friend"].get_value()
        task.info.guided = input_dict["guided"].get_value() == "1"
        task.info.ia_concept = input_dict["concept"].get_value() == "1"
        task.info.ia_code = input_dict["code"].get_value() == "1"
        task.info.ia_debug = input_dict["debug"].get_value() == "1"
        task.info.ia_problem = input_dict["problem"].get_value() == "1"
        task.info.ia_refactor = input_dict["refactor"].get_value() == "1"
        task.info.set_study(input_dict["study"].get_value())

    def send_key_up(self):
        self._line = max(self._line - 1, 0)

    def send_key_down(self):
        self._line = min(self._line + 1, len(self.all_input_lines) - 1)

    def send_key(self, key: int):
        self.all_input_lines[self._line].send_key(key)
        # self.change_task()
    
    def process_input(self, key: int) -> int:

        if key == curses.KEY_UP:
            self.send_key_up()
        elif key == curses.KEY_DOWN or key == ord("\t"):
            self.send_key_down()
        elif key == ord('\n'):
            if self._line != len(self.all_input_lines) - 1:
                self.send_key_down()
            else:
                self.floating.enable = False
                self.change_task(self._task, self.input_dict)
                if self.fn_exit is not None:
                    self.fn_exit(self._task)
        elif key == curses.KEY_EXIT:
            self.floating.enable = False
        else:
            self.send_key(key)
        return -1