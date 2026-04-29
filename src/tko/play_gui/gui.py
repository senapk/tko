from tko.config.settings import Settings
from tko.config.app_settings import AppSettings
from tko.widget.border import Border
from tko.widget.fmt import Fmt
from tko.widget.frame import Frame
from tko.floating.floating_manager import FloatingManager
from tko.play_tree.formatter_util import FormatterUtil
from tko.play.language_setter import LanguageSetter
from tko.play.search import Search
from tko.play_tree.task_tree import TaskTree

from tko.play_gui.gui_action_resolver import GuiActionResolver
from tko.play_gui.gui_left_panel import GuiLeftPanel
from tko.play_gui.gui_bottom_bar import GuiBottomBar
from tko.play_gui.gui_top_bar import GuiTopBar
from tko.play_gui.gui_skills_bar import GuiSkillsBar
from tko.play_gui.gui_help_panel import GuiHelpPanel
from tko.play_gui.gui_graph_panel import GuiGraphPanel
from tko.game.task import Task


class Gui:

    def __init__(self, tree: TaskTree, fman: FloatingManager):
        self.repo = tree.repo
        self.game = tree.game
        self.tree = tree
        self.flags = self.repo.flags
        self.fman = fman
        self.settings: Settings = tree.settings
        self.search = Search(tree=self.tree, fman=self.fman)
        self.style: Border = Border(self.settings.app)
        self.language = LanguageSetter(self.settings, self.repo, self.fman)
        self.colors = self.settings.colors
        self.app: AppSettings = self.settings.app

        self._need_update: bool = False
        self.fmt_util: FormatterUtil = FormatterUtil(self.settings, self.repo)

        # Sub-renderizadores
        self.action_resolver = GuiActionResolver(self.tree, self.fman, self.fmt_util, self.flags)
        self.left_panel      = GuiLeftPanel(self.tree, self.search, lambda: self._need_update)
        self.bottom_bar      = GuiBottomBar(self.tree, self.action_resolver)
        self.top_bar         = GuiTopBar(self.flags, self.app)
        self.skills_bar      = GuiSkillsBar(self.game, self.style, self.colors, self.flags)
        self.help_panel      = GuiHelpPanel()
        self.graph_panel     = GuiGraphPanel(self.settings, self.repo, self.flags)

    # ------------------------------------------------------------------
    # Estado público usado por play.py e play_actions.py
    # ------------------------------------------------------------------

    @property
    def xray_offset(self) -> int:
        return self.graph_panel.xray_offset

    @xray_offset.setter
    def xray_offset(self, value: int) -> None:
        self.graph_panel.xray_offset = value

    def set_need_update(self) -> None:
        self._need_update = True

    # ------------------------------------------------------------------
    # Delegações para compatibilidade com play_actions.py
    # ------------------------------------------------------------------

    def get_task_action(self, task: Task) -> tuple[str, str]:
        return self.action_resolver.get_task_action(task)

    def get_activate_label(self) -> tuple[str, str]:
        return self.action_resolver.get_activate_label()

    # ------------------------------------------------------------------
    # Ponto único de entrada de renderização
    # ------------------------------------------------------------------

    def _get_frame_color(self) -> str:
        if self.flags.task_view_mode.is_inbox():
            return "g"
        if self.flags.task_view_mode.is_all():
            return "y"
        return ""

    def show_items(self) -> None:
        border_color = self._get_frame_color()
        Fmt.clear()
        lines, cols = Fmt.get_size()
        main_sx = cols
        main_sy = lines

        top_y    = -1
        top_dy   = 1
        bottom_dy = 1
        mid_y    = top_dy
        mid_sy   = main_sy - top_dy - bottom_dy

        right_sx = 0
        if self.flags.show_panel.is_true():
            right_sx = round(cols * (100 - self.settings.app.panel_size_percent) / 100.0)

        task_sx = main_sx - right_sx

        frame_top = Frame(top_y, 0).set_size(top_dy + 2, cols)
        self.top_bar.show(frame_top)

        if self.flags.show_panel.is_true():
            frame_right = (
                Frame(mid_y, cols - right_sx)
                .set_size(mid_sy, right_sx)
                .set_border_color(self._get_frame_color())
            )
            if self.flags.panel.is_skills():
                self.skills_bar.show(frame_right)
            elif self.flags.panel.is_graph() or self.flags.panel.is_logs():
                try:
                    selected = self.tree.get_selected_throw()
                except IndexError:
                    selected = None
                self.graph_panel.show(frame_right, selected)
            elif self.flags.panel.is_help():
                self.help_panel.show(frame_right)

        # frame principal — desenhado após o painel lateral
        frame_main = (
            Frame(mid_y, 0)
            .set_size(mid_sy, task_sx)
            .set_border_color(border_color)
            .set_border_color(self._get_frame_color())
        )
        self.left_panel.show(frame_main)
        self.bottom_bar.show()
