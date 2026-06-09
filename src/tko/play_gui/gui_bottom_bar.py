from tko.game.task import Task
from tko.play_gui.gui_action_resolver import GuiActionResolver
from tko.play.keys import GuiActions, GuiKeys
from tko.play_tree.task_tree import TaskTree
from tko.util.rt import RT
from tko.widget.fmt import Fmt


class GuiBottomBar:

    def __init__(self, tree: TaskTree, action_resolver: GuiActionResolver):
        self.tree = tree
        self.action_resolver = action_resolver

    def show(self) -> None:
        lines, cols = Fmt.get_lines_cols()
        self_color = "X"
        try:
            selected = self.tree.get_selected_throw()
            if isinstance(selected, Task):
                self_color = "G"
        except IndexError:
            pass
        act_color, act_text = self.action_resolver.get_activate_label()
        help_fixed: list[RT] = [
            RT(f" {GuiActions.leave} ", "R"),
            RT(f" {GuiActions.create_draft} [{GuiKeys.create_draft}] ", "C"),
            RT(f" {GuiActions.pallete} [{GuiKeys.palette}] ", "C"),
            RT(f" {GuiActions.search} [{GuiKeys.search}] ", "G"),
            RT(f" {act_text} [↲] ", act_color),
            RT(f" {GuiActions.grade} [{GuiKeys.self_evaluate}] ", self_color),
        ]
        line_main = RT.join(help_fixed, RT(" "))
        Fmt.write(lines - 1, 0, line_main.center(cols))
