from __future__ import annotations
from tko.floating.floating import FloatingABC, Floating
from tko.game.task import Task
from tko.util.rtext import RText
from tko.util.symbols import Symbols
from tko.i18n import MsgKey, t

from abc import ABC, abstractmethod
from typing import Callable

import curses


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
        return RText(Symbols.right_triangle_filled if self.focus else " ") + " "

    @abstractmethod
    def send_key(self, key: int) -> None:
        pass

    def set_focus(self, focus: bool) -> InputLine:
        self.focus = focus
        return self

    @abstractmethod
    def get_text(self, pad: int) -> RText:
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
    def __init__(self, id: str, prefix: RText, opt_msgs: list[tuple[str, RText]], index: int = 0):
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

    def get_text(self, pad: int) -> RText:
        color = self.get_selected_color() if self.focus else ""
        text = self.get_opening() + self.prefix.set_style(color) + " "
        for i, c in enumerate(self.opt_msgs):
            opt, _ = c
            text += RText(opt, self.CHOOSEN_COLOR if i == self.index else "")
        text = text.ljust(pad)
        text += " ├" + self.opt_msgs[self.index][1]
        return text


class InputText(InputLine):
    def __init__(self, id: str, prompt: RText, text: str = ""):
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

    def get_text(self, pad: int) -> RText:
        data = (self.get_opening() + self.prompt.set_style(self.get_selected_color() if self.focus else "")).ljust(pad) + " "
        data = data + "├ " + RText(self.text, self.CHOOSEN_COLOR) + (Symbols.cursor if self.focus else "")
        return data


class InputBoolean(InputLine):
    def __init__(self, id: str, prefix: RText, start_value: str):
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

    def get_text(self, pad: int) -> RText:
        color = self.get_selected_color() if self.focus else ""
        text = self.get_opening()
        if self.focus:
            text += self.prefix.set_style(color)
        else:
            text += self.prefix
        text = text.ljust(pad) + "│ "
        text += RText(t(MsgKey.GRADE_NO), self.CHOOSEN_COLOR if self.value == "0" else "") + " " + RText(t(MsgKey.GRADE_YES), self.CHOOSEN_COLOR if self.value == "1" else "")
        return text


class FloatingGrade(FloatingABC):
    def __init__(self, task: Task, fn_exit: Callable[[Task], None] | None = None):
        self.floating = Floating()
        self._task = task
        self._line = 0
        self.floating.set_text_ljust()
        self.floating.frame.set_border_color("g")
        self.floating.set_header_text(RText(t(MsgKey.GRADE_HEADER), "y/"))
        self.floating.set_footer_text(RText(t(MsgKey.GRADE_FOOTER), "y/"))
        self.fn_exit = fn_exit

        progression: list[tuple[str, RText]] = [
            ("x", RText(t(MsgKey.GRADE_NOTHING), "g")),
            ("1", RText(" 10%", "y")),
            ("2", RText(" 20%", "y")),
            ("3", RText(" 30%", "y")),
            ("4", RText(" 40%", "y")),
            ("5", RText(" 50%", "y")),
            ("6", RText(" 60%", "y")),
            ("7", RText(" 70%", "y")),
            ("8", RText(" 80%", "y")),
            ("9", RText(" 90%", "y")),
            ("✓", RText(" 100%", "y"))]

        if self._task.config.is_auto:
            texto_auto = t(MsgKey.GRADE_AUTO_MODE_LABEL)
        else:
            texto_auto = t(MsgKey.GRADE_MANUAL_MODE_LABEL)
        
        guided   = "" if not self._task.info.feedback else ("1" if self._task.info.guided else "0")
        concept  = "" if not self._task.info.feedback else ("1" if self._task.info.ia_concept else "0")
        problem  = "" if not self._task.info.feedback else ("1" if self._task.info.ia_problem else "0")
        code     = "" if not self._task.info.feedback else ("1" if self._task.info.ia_code else "0")
        debug    = "" if not self._task.info.feedback else ("1" if self._task.info.ia_debug else "0")
        refactor = "" if not self._task.info.feedback else ("1" if self._task.info.ia_refactor else "0")

        self.quantity_input_lines: list[InputLine] = [
            InputSlide("rate", RText(texto_auto), progression, self._task.info.rate // 10).set_locked(self._task.config.is_auto),
            InputText("study", RText(t(MsgKey.GRADE_STUDY_TIME_LABEL)), str(self._task.info.study)).set_number_only(True),
        ]
        self.support_input_lines: list[InputLine] = [
            InputText("friend", RText(t(MsgKey.GRADE_FRIEND_LABEL)), self._task.info.friend),
            InputBoolean("guided",  RText(t(MsgKey.GRADE_GUIDED_LABEL)) + "      " + RText("   " + t(MsgKey.GRADE_GUIDED_DISCOUNT), "g") + self.get_discount("guided"), guided),
        ]
        self.quality_input_lines: list[InputLine] = [
            InputBoolean("concept", RText(t(MsgKey.GRADE_CONCEPT_LABEL)) + "" + RText("  " + t(MsgKey.GRADE_CONCEPT_DISCOUNT), "g") + self.get_discount("concept"), concept),
            InputBoolean("problem", RText(t(MsgKey.GRADE_PROBLEM_LABEL)) + "              " + RText(" " + t(MsgKey.GRADE_PROBLEM_DISCOUNT), "g") + self.get_discount("problem"), problem),
            InputBoolean("code",    RText(t(MsgKey.GRADE_CODE_LABEL)) + " " + RText(" " + t(MsgKey.GRADE_CODE_DISCOUNT), "g") + self.get_discount("code"), code),
            InputBoolean("debug",   RText(t(MsgKey.GRADE_DEBUG_LABEL)) + " " + RText("  " + t(MsgKey.GRADE_DEBUG_DISCOUNT), "g") + self.get_discount("debug"), debug),
            InputBoolean("refactor",RText(t(MsgKey.GRADE_REFACTOR_LABEL)) + "    " + RText("" + t(MsgKey.GRADE_REFACTOR_DISCOUNT), "g") + self.get_discount("refactor"), refactor),
        ]
        self.all_input_lines: list[InputLine] = self.quantity_input_lines + self.support_input_lines + self.quality_input_lines
        self.input_dict: dict[str, InputLine] = {line.id: line for line in self.all_input_lines}

    def get_discount(self, tag: str) -> RText:
        grade_dict = self._task.grader.grades
        value = grade_dict.get(self._task.config.loss.value, {}).get(tag, 100)
        size = 5
        if value == 100:
            return RText(" " * size, "g")
        else:
            return RText(f"-{100 - value}%".ljust(size), "y")

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
        content.append(RText(f"         {t(MsgKey.GRADE_SECTION_TITLE)}         "))
        width = 90
        pad = 66
        dummy_task = self._task.clone()
        self.change_task(dummy_task, self.input_dict)
        full_percent = dummy_task.grader.full_percent
        somatorio = RText(f'{round(full_percent):>3}% ', 'g')

        content.append(RText("╔") + (RText(" Tarefa:") + somatorio).center(width, "═"))
        left_side = "║ "
        for line in self.quantity_input_lines:
            content.append(RText(left_side) + line.get_text(pad))
        content.append(RText("╠═") + RText(f" {t(MsgKey.GRADE_SECTION_HUMAN_HELP)} ").center(width, "═"))
        for line in self.support_input_lines:
            content.append(RText(left_side) + line.get_text(pad))
        content.append(RText("╠═") + RText(f" {t(MsgKey.GRADE_SECTION_AI_USAGE)} ").center(width, "═"))
        for line in self.quality_input_lines:
            content.append(RText(left_side) + line.get_text(pad))
        content.append(RText("╚═══════════════════════════════════════════════════════════").ljust(width, "═"))

    def draw(self):
        self.update_content()
        self.floating.draw()

    @staticmethod
    def change_task(task: Task, input_dict: dict[str, InputLine]):
        if not task.config.is_auto:
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
