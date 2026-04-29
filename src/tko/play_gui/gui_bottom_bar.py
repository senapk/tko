from tko.game.task import Task
from tko.play_gui.gui_action_resolver import GuiActionResolver
from tko.play.keys import GuiActions, GuiKeys
from tko.play_tree.task_tree import TaskTree
from tko.util.rtext import RText
from tko.widget.fmt import Fmt


class GuiBottomBar:

    def __init__(self, tree: TaskTree, action_resolver: GuiActionResolver):
        self.tree = tree
        self.action_resolver = action_resolver

    def show(self) -> None:
        lines, cols = Fmt.get_size()
        self_color = "X"
        try:
            selected = self.tree.get_selected_throw()
            if isinstance(selected, Task):
                self_color = "G"
        except IndexError:
            pass
        act_color, act_text = self.action_resolver.get_activate_label()
        help_fixed: list[RText] = [
            RText(f" Sair [esc] ", "R"),
            RText(f" Criar Rascunho [{GuiKeys.create_draft}] ", "C"),
            RText(f" {GuiActions.pallete} [{GuiKeys.palette}] ", "C"),
            RText(f" {GuiActions.search} [{GuiKeys.search}] ", "G"),
            RText(f" {act_text} [↲] ", act_color),
            RText(f" {GuiActions.grade} [{GuiKeys.self_evaluate}] ", self_color),
        ]
        line_main = RText.join(help_fixed, RText(" "))
        Fmt.write(lines - 1, 0, line_main.center(cols))
