from tko.config.settings import Settings
from tko.config.app_settings import AppSettings
from tko.game.task import Task
from tko.i18n.message import Msg
from tko.repository.repository_watcher import RepositoryWatcher
from tko.widget.fmt import Fmt
from tko.widget.frame import Frame
from tko.floating.floating_manager import FloatingManager
from tko.play.language_setter import LanguageSetter
from tko.play.search import Search
from tko.play_tree.task_tree import TaskTree
from tko.repository.repository import Repository
from tko.play.flags import Flags
from tko.game.game import Game

from tko.play_gui.gui_action_resolver import GuiActionResolver
from tko.play_gui.gui_left_panel import GuiLeftPanel
from tko.play_gui.gui_bottom_bar import GuiBottomBar
from tko.play_gui.gui_top_bar import GuiTopBar
from tko.play_gui.gui_skills_bar import GuiSkillsBar
from tko.play_gui.gui_graph_panel import GuiGraphPanel


class Gui:

    def __init__(self, tree: TaskTree, fman: FloatingManager, watcher: RepositoryWatcher | None):
        self.repo: Repository = tree.repo
        self.game: Game = tree.game
        self.tree: TaskTree = tree
        self.flags: Flags = self.repo.flags
        self.fman: FloatingManager = fman
        self.settings: Settings = tree.settings
        self.search = Search(tree=self.tree, fman=self.fman)
        self.language = LanguageSetter(self.settings, self.repo, self.fman)
        self.colors = self.settings.colors
        self.app: AppSettings = self.settings.app
        self.watcher = watcher

        top_floating = lambda: self.fman.get_top()
        in_search = lambda: self.search.search_mode
        self._need_update: bool = False

        # Sub-renderizadores
        self.action_resolver = GuiActionResolver(self.tree, self.fman, self.tree.task_formatter, self.flags)
        self.left_panel      = GuiLeftPanel(self.tree, self.search, lambda: self._need_update)
        self.bottom_bar      = GuiBottomBar(self.tree, self.action_resolver, in_search, top_floating)

        edit_mode_fn = lambda: self.watcher is not None and self.watcher.edit_logger is not None
        audit_mode_fn = lambda: self.watcher is not None and self.watcher.audit_logger is not None
        
        self.top_bar         = GuiTopBar(self.flags, self.app, edit_fn=edit_mode_fn, audit_fn=audit_mode_fn)
        self.skills_bar      = GuiSkillsBar(self.game, self.colors, self.flags, lambda: self.tree.get_selected_throw().basic.remote_name)
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

    def get_task_action(self, tr: Task) -> tuple[str, Msg]:
        return self.action_resolver.get_task_action(tr)

    def get_activate_label(self) -> tuple[str, Msg]:
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
        lines, cols = Fmt.get_lines_cols()
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

        # frame principal — desenhado após o painel lateral
        frame_main = (
            Frame(mid_y, 0)
            .set_size(mid_sy, task_sx)
            .set_border_color(border_color)
            .set_border_color(self._get_frame_color())
        )
        self.left_panel.show(frame_main)
        self.bottom_bar.show()
