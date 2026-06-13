from tko.config.app_settings import AppSettings
from tko.widget.frame import Frame
from tko.config.flags import Flags
from tko.play.gui_keys import GuiKeys
from tko.util.rt import RT
from tko.widget.button import Button
from tko.i18n import Msg
import time

class _TopBarMsg:
    RECOMMENDED = Msg(pt="Recomendadas", en="Recommended")
    ALL = Msg(pt="Todas", en="All")
    GRAPHS = Msg(pt="Gráficos", en="Graphs")
    LOGS = Msg(pt="Logs", en="Logs")
    SKILLS = Msg(pt="Trilhas", en="Skills")
    HELP = Msg(pt="Ajuda", en="Help")


class GuiTopBar:

    def get_time_hhmmss(self) -> RT:
        return Button.info_label(time.strftime("%H:%M:%S"))


    def __init__(self, flags: Flags, app: AppSettings):
        self.flags = flags
        self.app = app

    def show(self, frame: Frame) -> None:
        panel_on = self.flags.show_panel.is_true()
        vi = Button()
        pre = [
            vi.toggle_bt(f"{str(_TopBarMsg.RECOMMENDED)}[{GuiKeys.inbox}]", self.flags.task_view_mode.is_inbox()),
            vi.toggle_bt(f"{str(_TopBarMsg.ALL)}[{GuiKeys.all_tasks}]", self.flags.task_view_mode.is_all()),
            RT(" "),
        ]
        pos = [
            vi.toggle_bt(f"{str(_TopBarMsg.GRAPHS)}[{GuiKeys.panel_graph}]", panel_on and self.flags.panel.is_graph()),
            vi.toggle_bt(f"{str(_TopBarMsg.LOGS)}[{GuiKeys.panel_logs}]", panel_on and self.flags.panel.is_logs()),
            vi.toggle_bt(f"{str(_TopBarMsg.SKILLS)}[{GuiKeys.panel_skills}]", panel_on and self.flags.panel.is_skills()),
        ]


        limit = frame.get_dx()

        left = RT.join(pre, " ")
        center = self.get_time_hhmmss()
        right = RT.join(pos, RT(" "))

        # Calculate available space for center
        # if possible center the time, otherwise align to the left of the remaining space
        # if the time doesn't fit, remove it and just show the buttons
        space_for_center = limit - len(left) - len(right)
        if space_for_center < len(center):
            center = RT("")
        frame.write(0, 0, left)
        right_space_start = limit - len(left)
        if right_space_start < len(left):
            right_space_start = len(left) + 1
        else:
            right_space_start = limit - len(right)
        frame.write(0, right_space_start, right)

        available = limit - len(left) - len(right)
        if available < len(center):
            return
        frame.write(0, len(left), center.center(available))
