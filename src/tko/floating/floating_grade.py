from __future__ import annotations
from tko.floating.floating import FloatingABC, Floating
from tko.game.task import Task
from tko.util.rbuffer import RBuffer
from tko.util.rt import RT
from tko.util.symbols import Symbols
from tko.i18n import Msg

from abc import ABC, abstractmethod
from typing import Callable

import curses


class _GradeMsg:
    NO = Msg(pt="Não", en="No")
    YES = Msg(pt="Sim", en="Yes")
    HEADER = Msg(pt=" Utilize os direcionais e texto para marcar", en=" Use arrow keys and text to mark")
    FOOTER = Msg(pt=" Pressione Enter para confirmar, Esc para cancelar", en=" Press Enter to confirm, Esc to cancel")
    NOTHING = Msg(pt=" Nada", en=" Nothing")

    AUTO_MODE_LABEL = Msg(pt="Taxa de testes que passou na última execução:", en="Percentage of tests that passed in the last run:")
    MANUAL_MODE_LABEL = Msg(pt="Informe qual percentual da atividade você fez?", en="What percentage of the activity did you complete?")
    STUDY_TIME_LABEL = Msg(pt="Qual tempo total estimado, estudo + código, em minutos?", en="What is the total estimated time, study + code, in minutes?")
    FRIEND_LABEL = Msg(pt="Deixe em branco se fez sozinho, ou com o nome de quem ajudou", en="Leave blank if you did it alone, or with the name of who helped")
    GUIDED_LABEL = Msg(pt="Fez o código copiando da aula ou vídeo aula?", en="Did you code by copying from class or video?")
    CONCEPT_LABEL = Msg(pt="ESTUDAR conceitos sem gerar a solução do problema?", en="STUDY concepts without generating the problem solution?")
    PROBLEM_LABEL = Msg(pt="ENTENDER o problema a ser resolvido?", en="UNDERSTAND the problem to be solved?")
    CODE_LABEL = Msg(pt="GERAR ou CORRIGIR código relacionado ao problema?", en="GENERATE or FIX code related to the problem?")
    DEBUG_LABEL = Msg(pt="COMPREENDER mensagens de ERRO ou SAÍDA incorreta?", en="UNDERSTAND ERROR messages or incorrect OUTPUT?")
    REFACTOR_LABEL = Msg(pt="REFATORAR o código só após fazer tudo sozinho?", en="REFACTOR code only after doing everything yourself?")

    GUIDED_DISCOUNT = Msg(pt="COPIOU:", en="COPIED:")
    CONCEPT_DISCOUNT = Msg(pt="ESTUDAR:", en="STUDY:")
    PROBLEM_DISCOUNT = Msg(pt="ENTENDER:", en="UNDERSTAND:")
    CODE_DISCOUNT = Msg(pt="CORRIGIR:", en="FIX:")
    DEBUG_DISCOUNT = Msg(pt="DEBUGAR:", en="DEBUG:")
    REFACTOR_DISCOUNT = Msg(pt="REFATORAR:", en="REFACTOR:")

    SECTION_TITLE = Msg(
        pt="Pontue de acordo com a última vez que você (re)fez a tarefa do zero (sprint)",
        en="Rate according to the last time you (re)did the task from scratch (sprint)",
    )
    SECTION_HUMAN_HELP = Msg(pt="Você fez com ajuda humana ou guiado?", en="Did you do it with human help or guided?")
    SECTION_AI_USAGE = Msg(pt="Você usou IA (LLMs) para", en="Did you use AI (LLMs) for")


_GRADE_LABELS = (
    _GradeMsg.AUTO_MODE_LABEL,
    _GradeMsg.MANUAL_MODE_LABEL,
    _GradeMsg.STUDY_TIME_LABEL,
    _GradeMsg.FRIEND_LABEL,
    _GradeMsg.GUIDED_LABEL,
    _GradeMsg.CONCEPT_LABEL,
    _GradeMsg.PROBLEM_LABEL,
    _GradeMsg.CODE_LABEL,
    _GradeMsg.DEBUG_LABEL,
    _GradeMsg.REFACTOR_LABEL,
)
_GRADE_LABEL_WIDTH = max(max(len(label.pt), len(label.en)) for label in _GRADE_LABELS)
_GRADE_LINE_PAD = _GRADE_LABEL_WIDTH + 10


class InputLine(ABC):
    SELECTED_COLOR = "X"
    LOCKED_COLOR = "r"
    CHOOSEN_COLOR = "X"

    def __init__(self, id: str):
        self.id = id
        self.locked = False
        self.focus = False

    def get_selected_color(self) -> str:
        if self.locked:
            return self.LOCKED_COLOR
        return self.SELECTED_COLOR

    def get_opening(self):
        return RT(Symbols.right_triangle_filled if self.focus else " ") + " "

    @abstractmethod
    def send_key(self, key: int) -> None:
        pass

    def set_focus(self, focus: bool) -> InputLine:
        self.focus = focus
        return self

    @abstractmethod
    def get_text(self, pad: int) -> RT:
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
    def __init__(self, id: str, prefix: RT, opt_msgs: list[tuple[str, RT]], index: int = 0):
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

    def get_text(self, pad: int) -> RT:
        color = self.get_selected_color() if self.focus else ""
        text_buffer = RBuffer().add(self.get_opening()).add(self.prefix.set_style(color)).add(" ")
        for i, c in enumerate(self.opt_msgs):
            opt, _ = c
            text_buffer.add(opt, self.CHOOSEN_COLOR if i == self.index else "")
        text = text_buffer.to_rt()
        text = text.ljust(pad)
        text += "├" + self.opt_msgs[self.index][1]
        return text


class InputText(InputLine):
    def __init__(self, id: str, prompt: RT, text: str = ""):
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

    def get_text(self, pad: int) -> RT:
        data = (self.get_opening() + self.prompt.set_style(self.get_selected_color() if self.focus else "")).ljust(pad)
        data = data + "├ " + RT(self.text, self.CHOOSEN_COLOR) + (Symbols.cursor if self.focus else "")
        return data


class InputBoolean(InputLine):
    def __init__(self, id: str, prefix: RT, start_value: str):
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

    def get_text(self, pad: int) -> RT:
        color = self.get_selected_color() if self.focus else ""
        text_buffer = RBuffer().add(self.get_opening())
        if self.focus:
            text_buffer.add(self.prefix.set_style(color))
        else:
            text_buffer.add(self.prefix)
        text = text_buffer.to_rt().ljust(pad)
        text_buffer = RBuffer().add(text).add("│ ")
        text_buffer.add(str(_GradeMsg.NO), self.CHOOSEN_COLOR if self.value == "0" else "")
        text_buffer.add(" ")
        text_buffer.add(str(_GradeMsg.YES), self.CHOOSEN_COLOR if self.value == "1" else "")
        return text_buffer.to_rt()


class FloatingGrade(FloatingABC):
    def __init__(self, task: Task, fn_exit: Callable[[Task], None] | None = None):
        super().__init__()
        self.floating = Floating()
        self._task = task
        self._line = 0
        self.floating.set_text_ljust()
        self.floating.frame.set_border_color("g")
        self.floating.set_header_text(RT(str(_GradeMsg.HEADER), "y/"))
        self.floating.set_footer_text(RT(str(_GradeMsg.FOOTER), "y/"))
        self.fn_exit = fn_exit

        progression: list[tuple[str, RT]] = [
            ("x", RT(str(_GradeMsg.NOTHING), "g")),
            ("1", RT(" 10%", "y")),
            ("2", RT(" 20%", "y")),
            ("3", RT(" 30%", "y")),
            ("4", RT(" 40%", "y")),
            ("5", RT(" 50%", "y")),
            ("6", RT(" 60%", "y")),
            ("7", RT(" 70%", "y")),
            ("8", RT(" 80%", "y")),
            ("9", RT(" 90%", "y")),
            ("✓", RT(" 100%", "y"))]

        if self._task.config.is_eval_test:
            texto_auto = str(_GradeMsg.AUTO_MODE_LABEL)
        else:
            texto_auto = str(_GradeMsg.MANUAL_MODE_LABEL)
        
        guided   = "" if not self._task.info.feedback else ("1" if self._task.info.guided else "0")
        concept  = "" if not self._task.info.feedback else ("1" if self._task.info.ia_concept else "0")
        problem  = "" if not self._task.info.feedback else ("1" if self._task.info.ia_problem else "0")
        code     = "" if not self._task.info.feedback else ("1" if self._task.info.ia_code else "0")
        debug    = "" if not self._task.info.feedback else ("1" if self._task.info.ia_debug else "0")
        refactor = "" if not self._task.info.feedback else ("1" if self._task.info.ia_refactor else "0")

        self.quantity_input_lines: list[InputLine] = [
            InputSlide("rate", RT(texto_auto), progression, self._task.info.rate // 10).set_locked(self._task.config.is_eval_test),
            InputText("study", RT(str(_GradeMsg.STUDY_TIME_LABEL)), str(self._task.info.study)).set_number_only(True),
        ]
        self.support_input_lines: list[InputLine] = [
            InputText("friend", RT(str(_GradeMsg.FRIEND_LABEL)), self._task.info.friend),
            InputBoolean("guided",  RT(str(_GradeMsg.GUIDED_LABEL)) + "      " + RT("   " + str(_GradeMsg.GUIDED_DISCOUNT), "g") + self.get_discount("guided"), guided),
        ]
        self.quality_input_lines: list[InputLine] = [
            InputBoolean("concept", RT(str(_GradeMsg.CONCEPT_LABEL)) + "" + RT("  " + str(_GradeMsg.CONCEPT_DISCOUNT), "g") + self.get_discount("concept"), concept),
            InputBoolean("problem", RT(str(_GradeMsg.PROBLEM_LABEL)) + "              " + RT(" " + str(_GradeMsg.PROBLEM_DISCOUNT), "g") + self.get_discount("problem"), problem),
            InputBoolean("code",    RT(str(_GradeMsg.CODE_LABEL)) + " " + RT(" " + str(_GradeMsg.CODE_DISCOUNT), "g") + self.get_discount("code"), code),
            InputBoolean("debug",   RT(str(_GradeMsg.DEBUG_LABEL)) + " " + RT("  " + str(_GradeMsg.DEBUG_DISCOUNT), "g") + self.get_discount("debug"), debug),
            InputBoolean("refactor",RT(str(_GradeMsg.REFACTOR_LABEL)) + "    " + RT("" + str(_GradeMsg.REFACTOR_DISCOUNT), "g") + self.get_discount("refactor"), refactor),
        ]
        self.all_input_lines: list[InputLine] = self.quantity_input_lines + self.support_input_lines + self.quality_input_lines
        self.input_dict: dict[str, InputLine] = {line.id: line for line in self.all_input_lines}

    def get_discount(self, tag: str) -> RT:
        grade_dict = self._task.grader.grades
        value = grade_dict.get(self._task.config.loss.value, {}).get(tag, 100)
        size = 5
        if value == 100:
            return RT(" " * size, "g")
        else:
            return RT(f"-{100 - value}%".ljust(size), "y")

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
        content.append(RT(f"         {str(_GradeMsg.SECTION_TITLE)}         "))
        width = 90
        pad = _GRADE_LINE_PAD
        dummy_task = self._task.clone()
        self.change_task(dummy_task, self.input_dict)
        full_percent = dummy_task.grader.full_percent
        somatorio = RT(f'{round(full_percent):>3}% ', 'g')

        content.append(RT("╔") + (RT(" Tarefa:") + somatorio).center(width, "═"))
        left_side = "║ "
        for line in self.quantity_input_lines:
            content.append(RT(left_side) + line.get_text(pad))
        content.append(RT("╠═") + RT(f" {str(_GradeMsg.SECTION_HUMAN_HELP)} ").center(width, "═"))
        for line in self.support_input_lines:
            content.append(RT(left_side) + line.get_text(pad))
        content.append(RT("╠═") + RT(f" {str(_GradeMsg.SECTION_AI_USAGE)} ").center(width, "═"))
        for line in self.quality_input_lines:
            content.append(RT(left_side) + line.get_text(pad))
        content.append(RT("╚═══════════════════════════════════════════════════════════").ljust(width, "═"))

    def draw(self):
        self.update_content()
        self.floating.draw()

    @staticmethod
    def change_task(task: Task, input_dict: dict[str, InputLine]):
        if not task.config.is_eval_test:
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
