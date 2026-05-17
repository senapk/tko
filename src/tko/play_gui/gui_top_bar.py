from tko.config.app_settings import AppSettings
from tko.widget.frame import Frame
from tko.config.flags import Flags
from tko.play.keys import GuiKeys
from tko.util.rtext import RText
from tko.util.visual import Visual
from tko.i18n import MsgKey, t


class GuiTopBar:

    def __init__(self, flags: Flags, app: AppSettings):
        self.flags = flags
        self.app = app

    def show(self, frame: Frame) -> None:
        panel_on = self.flags.show_panel.is_true()
        vi = Visual(self.app.use_borders)
        pre = [
            vi.render_button(f"{t(MsgKey.GUI_TOP_BAR_RECOMMENDED)}[{GuiKeys.inbox}]", self.flags.task_view_mode.is_inbox()),
            vi.render_button(f"{t(MsgKey.GUI_TOP_BAR_ALL)}[{GuiKeys.all_tasks}]", self.flags.task_view_mode.is_all()),
            RText(" "),
        ]
        pos = [
            vi.render_button(f"{t(MsgKey.GUI_TOP_BAR_GRAPHS)}[{GuiKeys.panel_graph}]", panel_on and self.flags.panel.is_graph()),
            vi.render_button(f"{t(MsgKey.GUI_TOP_BAR_LOGS)}[{GuiKeys.panel_logs}]", panel_on and self.flags.panel.is_logs()),
            vi.render_button(f"{t(MsgKey.GUI_TOP_BAR_SKILLS)}[{GuiKeys.panel_skills}]", panel_on and self.flags.panel.is_skills()),
            vi.render_button(f"{t(MsgKey.GUI_TOP_BAR_HELP)}[{GuiKeys.panel_help}]", panel_on and self.flags.panel.is_help()),
        ]
        last = [
            vi.render_button(f"{t(MsgKey.GUI_TOP_BAR_EXEC)}[PageUp]", self.flags.task_graph_mode.is_executions()),
            vi.render_button(f"{t(MsgKey.GUI_TOP_BAR_TIME)}[PgDown]", self.flags.task_graph_mode.is_time_view()),
        ]

        limit = frame.get_dx()
        extra = RText()
        if self.flags.panel.is_graph():
            extra = RText.join(last, RText(""))

        info = RText.join(pre + pos, RText(""))
        info = RText(" " * ((limit - len(info)) // 2)) + info
        info += RText(" " * (limit - len(info) - len(extra))) + extra
        frame.write(0, 1, info)
