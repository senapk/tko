from tko.config.app_settings import AppSettings
from tko.widget.frame import Frame
from tko.config.flags import Flags
from tko.play.gui_keys import GuiKeys
from tko.util.rt import RT
from tko.widget.button import Button
from tko.i18n import Msg
from typing import Callable
from tko.util.aligner import Aligner
import time

class _TopBarMsg:
    RECOMMENDED = Msg.text(pt="Recomendadas", en="Recommended")
    ALL = Msg.text(pt="Todas", en="All")
    GRAPHS = Msg.text(pt="Gráficos", en="Graphs")
    LOGS = Msg.text(pt="Logs", en="Logs")
    SKILLS = Msg.text(pt="Trilhas", en="Skills")


def get_loop_4() -> str:
    value = int(time.time())
    states = (
            "▄▄▄ ", 
            "█▄  ", 
            "█▀  ", 
            "▀▀▀ ", 
            " ▀▀▀", 
            "  ▀█", 
            "  ▄█", 
            " ▄▄▄", 
            )
    state = value % len(states)
    return states[state]

def get_loop_3() -> str:
    value = int(time.time())
    states = (
            "▄▄▄", 
            "█▄ ", 
            "█▀ ", 
            "▀▀▀", 
            " ▀█", 
            " ▄█", 
            )
    state = value % len(states)
    return states[state]

def get_loop_2() -> str:
    value = int(time.time())
    states = (
            "█▄", 
            "█▀", 
            "▀█", 
            "▄█", 
            )
    state = value % len(states)
    return states[state]

def edit_audit_info(edit_mode_fn: Callable[[], bool], audit_info_fn: Callable[[], bool], timed: bool) -> RT:
    output: list[RT] = []
    output.append(Button.toggle_bt("WATCH EDIT "+ ("ON" if edit_mode_fn() else "OFF"), active = edit_mode_fn(), enabled=edit_mode_fn()))
    timer = Button.info_label(get_loop_2(), color = "y", sep = "") if timed else RT("  ")
    output.append(timer)
    output.append(Button.toggle_bt("AUDIT MODE " + ("ON" if audit_info_fn() else "OFF"), active = audit_info_fn(), enabled=audit_info_fn()))
    return RT.join(output, "")

class GuiTopBar:

    def get_time_hhmmss(self) -> RT:
        return Button.info_label(time.strftime("%H:%M:%S"))

    def __init__(self, flags: Flags, app: AppSettings, audit_fn: Callable[[], bool], edit_fn: Callable[[], bool]):
        self.flags = flags
        self.app = app
        self.edit_mode_fn = edit_fn
        self.audit_info_fn = audit_fn


    def show(self, frame: Frame) -> None:
        vi = Button()
        pre = [
            vi.toggle_bt(f"{str(_TopBarMsg.RECOMMENDED)}[{GuiKeys.inbox}]", self.flags.task_view_mode.is_inbox()),
            vi.toggle_bt(f"{str(_TopBarMsg.ALL)}[{GuiKeys.all_tasks}]", self.flags.task_view_mode.is_all()),
        ]
        pos = [
            vi.toggle_bt(f"{str(_TopBarMsg.GRAPHS)}[{GuiKeys.panel_graph}]", self.flags.panel.is_graph()),
            vi.toggle_bt(f"{str(_TopBarMsg.LOGS)}[{GuiKeys.panel_logs}]", self.flags.panel.is_logs()),
            vi.toggle_bt(f"{str(_TopBarMsg.SKILLS)}[{GuiKeys.panel_skills}]", self.flags.panel.is_skills()),
        ]


        limit = frame.get_dx()

        left = RT.join(pre, " ")
        center = edit_audit_info(self.edit_mode_fn, self.audit_info_fn, timed=True)
        right = RT.join(pos, RT(" "))

        text = Aligner.distribute_with_filler(left, center, right, " ", limit)
        frame.write(0, 0, text)
