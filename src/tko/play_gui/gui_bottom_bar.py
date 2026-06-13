from tko.game.task import Task
from tko.play.gui_actions_names import GuiActionsNames
from tko.play_gui.gui_action_resolver import GuiActionResolver
from tko.play.gui_keys import GuiKeys
from tko.play_tree.task_tree import TaskTree
from tko.util.rt import RT
from tko.widget.fmt import Fmt
from tko.widget.button import Button
from tko.floating.floating import FloatingABC
from typing import Callable

class GuiBottomBar:

    def __init__(self, tree: TaskTree, action_resolver: GuiActionResolver, in_search: Callable[[], bool], top_floating_fn: Callable[[], FloatingABC | None]):
        self.tree = tree
        self.flags = tree.repo.flags
        self.action_resolver = action_resolver
        self.in_search = in_search
        self.top_floating_fn = top_floating_fn

    def show(self) -> None:
        top_floating = self.top_floating_fn()
        self.in_drafts = top_floating is not None and top_floating.id == "drafts"
        self.in_palette = top_floating is not None and top_floating.id == "palette"
        self.in_self = top_floating is not None and top_floating.id == "self"

        lines, cols = Fmt.get_lines_cols()
        self_enabled = False
        try:
            selected = self.tree.get_selected_throw()
            if isinstance(selected, Task):
                self_enabled = True
        except IndexError:
            pass

        button = Button().toggle_bt
        
        _, act_text = self.action_resolver.get_activate_label()
        in_help = self.flags.panel.is_help() and self.flags.show_panel.is_true()
        help_fixed: list[RT] = [
            button(f"{GuiActionsNames.create_draft} [{GuiKeys.create_draft}]", active=self.in_drafts),
            button(f"{GuiActionsNames.pallete} [{GuiKeys.palette}]", active=self.in_palette),
            button(f"{GuiActionsNames.search} [{GuiKeys.search}]", active=self.in_search()),
            button(f"{GuiActionsNames.help} [{GuiKeys.ask_help}]", active=in_help),
            Button.action_bt(f"{act_text} [↲]", enabled=True),
            Button.toggle_bt(f"{GuiActionsNames.grade} [{GuiKeys.self_evaluate}]", active=self.in_self, enabled=self_enabled),
        ]
        line_main = RT.join(help_fixed, RT(" "))
        Fmt.write(lines - 1, 0, line_main.center(cols))
