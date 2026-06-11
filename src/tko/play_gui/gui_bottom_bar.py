from tko.game.task import Task
from tko.play.gui_actions_names import GuiActionsNames
from tko.play_gui.gui_action_resolver import GuiActionResolver
from tko.play.gui_keys import GuiKeys
from tko.play_tree.task_tree import TaskTree
from tko.util.rt import RT
from tko.widget.fmt import Fmt
from typing import Callable


class GuiBottomBar:

    def __init__(self, tree: TaskTree, action_resolver: GuiActionResolver, 
                 in_drafts: Callable[[], bool], in_palette: Callable[[], bool], in_search_mode: Callable[[], bool]):
        self.tree = tree
        self.flags = tree.repo.flags
        self.action_resolver = action_resolver
        self.in_drafts = in_drafts
        self.in_palette = in_palette
        self.in_search = in_search_mode

    def show(self) -> None:
        lines, cols = Fmt.get_lines_cols()
        self_color = "X"
        try:
            selected = self.tree.get_selected_throw()
            if isinstance(selected, Task):
                self_color = "G"
        except IndexError:
            pass

        def button(value: bool):
            return "G" if value else "X"
        act_color, act_text = self.action_resolver.get_activate_label()
        in_help = self.flags.panel.is_help() and self.flags.show_panel.is_true()
        help_fixed: list[RT] = [
            RT(f" {GuiActionsNames.create_draft} [{GuiKeys.create_draft}] ", button(self.in_drafts())),
            RT(f" {GuiActionsNames.pallete} [{GuiKeys.palette}] ", button(self.in_palette())),
            RT(f" {GuiActionsNames.search} [{GuiKeys.search}] ", button(self.in_search())),
            RT(f" {GuiActionsNames.help} [{GuiKeys.panel_help}] ", button(in_help)),
            RT(f" {act_text} [↲] ", act_color),
            RT(f" {GuiActionsNames.grade} [{GuiKeys.self_evaluate}] ", self_color),
        ]
        line_main = RT.join(help_fixed, RT(" "))
        Fmt.write(lines - 1, 0, line_main.center(cols))
