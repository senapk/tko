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
    NO = Msg.text(pt="Não", en="No")
    YES = Msg.text(pt="Sim", en="Yes")
    HEADER = Msg.text(pt=" Utilize os direcionais e texto para marcar ", en=" Use arrow keys and text to mark ")
    FOOTER = Msg.text(pt=" Pressione Enter para confirmar, Esc para cancelar ", en=" Press Enter to confirm, Esc to cancel ")
    NOTHING = Msg.text(pt=" Nada", en=" Nothing")

    AUTO_MODE_LABEL = Msg.text(pt="Taxa de testes que passou na última execução:", en="Percentage of tests that passed in the last run:")
    MANUAL_MODE_LABEL = Msg.text(pt="Informe qual percentual da atividade você fez?", en="What percentage of the activity did you complete?")
    STUDY_TIME_LABEL = Msg.text(pt="Qual tempo total estimado, estudo + código, em minutos?", en="What is the total estimated time, study + code, in minutes?")

    BOSS_MODE_ON = Msg.parse(
        pt=
        "Escolhendo sim, você declara que realizou esta atividade sozinho, como se\n"
        "estivesse em um ambiente de avaliação, sem pesquisas ou ferramentas não\n"
        "autorizadas, e que todo o trabalho entregue, mesmo que parcial, foi produzido\n"
        "a partir do seu próprio conhecimento, por meio de tentativa e erro.",
        en=
        "By choosing yes, you declare that you performed this activity alone, as if\n"
        "you were in an evaluation environment, without research or unauthorized tools,\n"
        "and that all the work delivered, even if partial, was produced from your,\n"
        "own knowledge through trial and error."
    )

    BOSS_MODE_OFF = Msg.parse(
        pt=
        "Escolhendo não, você declara que a atividade não foi\n"
        "realizada integralmente nas condições de avaliação,\n"
        "podendo ter utilizado pesquisas, ajuda, ferramentas\n"
        "não autorizadas ou ferramentas de IA.",
        en=
        "By choosing no, you declare that the activity was not\n"
        "fully performed under evaluation conditions,\n"
        "and that you may have used research, help,\n"
        "unauthorized tools, or AI tools."
    )

    BOSS_MODE_LABEL = Msg.text(pt="Você realizou esta atividade em modo de avaliação?", 
                               en="Did you perform this activity in evaluation mode?")


    SECTION_TITLE = Msg.text(
        pt="Pontue de acordo com a última vez que você (re)fez a tarefa do zero (sprint)",
        en="Rate according to the last time you (re)did the task from scratch (sprint)",
    )


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
        return RT(">" if self.focus else " ") + " "

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
        self.floating.set_header_rt(RT(str(_GradeMsg.HEADER), "y/"))
        self.floating.set_footer_rt(RT(str(_GradeMsg.FOOTER), "y/"))
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
        

        all_input_lines: list[InputLine] = []
        all_input_lines.append(InputSlide("rate", RT(texto_auto), progression, self._task.info.rate // 10).set_locked(self._task.config.is_eval_test))
        all_input_lines.append(InputText("study", RT(str(_GradeMsg.STUDY_TIME_LABEL)), str(self._task.info.study)).set_number_only(True))
        boss_init = ""
        if self._task.info.feedback:
            boss_init = "1" if self._task.info.boss else "0"
        all_input_lines.append(InputBoolean("boss", RT(str(_GradeMsg.BOSS_MODE_LABEL)), boss_init))

        self.all_input_lines = all_input_lines
        self.input_dict: dict[str, InputLine] = {line.id: line for line in all_input_lines}

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
        # content.append(RT(f"         {str(_GradeMsg.SECTION_TITLE)}         "))
        width = 80
        pad = 60
        dummy_task = self._task.clone()
        self.change_task(dummy_task, self.input_dict)
        
        # content.append(RT("╔") + (RT(" Tarefa")).center(width, "═"))
        left_side = " "
        
        content.append(RT(left_side) + self.input_dict["rate"].get_text(pad))
        content.append(RT(left_side) + self.input_dict["study"].get_text(pad))
        content.append(RT(left_side) + self.input_dict["boss"].get_text(pad))
        content.append(RT("═") + RT(f" {str(Msg.text(pt='LEIA COM ATENÇÃO', en='READ CAREFULLY'))} ", "y").center(width, "═"))
        if self.input_dict["boss"].get_value() == "1":
            for line in _GradeMsg.BOSS_MODE_ON.pt.splitlines():
                content.append(RT(left_side) + line.center(width))
        elif self.input_dict["boss"].get_value() == "0":
            for line in _GradeMsg.BOSS_MODE_OFF.pt.splitlines():
                content.append(RT(left_side) + line.center(width))
        else:
            for _ in range(4):
                content.append(RT(""))

    def draw(self):
        self.update_content()
        self.floating.draw()

    @staticmethod
    def change_task(task: Task, input_dict: dict[str, InputLine]):
        if not task.config.is_eval_test:
            task.info.rate = int(input_dict["rate"].get_value()) * 10
        task.info.feedback = True

        task.info.set_study(input_dict["study"].get_value())
        task.info.boss = input_dict["boss"].get_value() == "1"

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
