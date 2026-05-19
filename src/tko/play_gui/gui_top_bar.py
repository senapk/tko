from tko.config.app_settings import AppSettings
from tko.widget.frame import Frame
from tko.config.flags import Flags
from tko.play.keys import GuiKeys
from tko.util.rt import RT
from tko.util.tab_renderer import TabRenderer
from tko.i18n import Msg, t


class _TopBarMsg:
    RECOMMENDED = Msg(pt="Recomendadas", en="Recommended")
    ALL = Msg(pt="Todas", en="All")
    GRAPHS = Msg(pt="Gráficos", en="Graphs")
    LOGS = Msg(pt="Logs", en="Logs")
    SKILLS = Msg(pt="Trilhas", en="Skills")
    HELP = Msg(pt="Ajuda", en="Help")
    EXEC = Msg(pt="Exec", en="Exec")
    TIME = Msg(pt="Time", en="Time")


class GuiTopBar:

    def __init__(self, flags: Flags, app: AppSettings):
        self.flags = flags
        self.app = app

    def show(self, frame: Frame) -> None:
        panel_on = self.flags.show_panel.is_true()
        vi = TabRenderer()
        pre = [
            vi.render_button(f"{t(_TopBarMsg.RECOMMENDED)}[{GuiKeys.inbox}]", self.flags.task_view_mode.is_inbox()),
            vi.render_button(f"{t(_TopBarMsg.ALL)}[{GuiKeys.all_tasks}]", self.flags.task_view_mode.is_all()),
            RT(" "),
        ]
        pos = [
            vi.render_button(f"{t(_TopBarMsg.GRAPHS)}[{GuiKeys.panel_graph}]", panel_on and self.flags.panel.is_graph()),
            vi.render_button(f"{t(_TopBarMsg.LOGS)}[{GuiKeys.panel_logs}]", panel_on and self.flags.panel.is_logs()),
            vi.render_button(f"{t(_TopBarMsg.SKILLS)}[{GuiKeys.panel_skills}]", panel_on and self.flags.panel.is_skills()),
            vi.render_button(f"{t(_TopBarMsg.HELP)}[{GuiKeys.panel_help}]", panel_on and self.flags.panel.is_help()),
        ]
        last = [
            vi.render_button(f"{t(_TopBarMsg.EXEC)}[PageUp]", self.flags.task_graph_mode.is_executions()),
            vi.render_button(f"{t(_TopBarMsg.TIME)}[PgDown]", self.flags.task_graph_mode.is_time_view()),
        ]

        limit = frame.get_dx()
        extra = RT()
        if self.flags.panel.is_graph():
            extra = RT.join(last, RT(""))

        info = RT.join(pre + pos, RT(""))
        info = RT(" " * ((limit - len(info)) // 2)) + info
        info += RT(" " * (limit - len(info) - len(extra))) + extra
        frame.write(0, 1, info)
