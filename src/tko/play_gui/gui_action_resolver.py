from tko.game.quest import Quest
from tko.game.task import Task
from tko.play.task_action import TaskAction
from tko.floating.floating_manager import FloatingManager
from tko.play_tree.formatter_util import FormatterUtil
from tko.play.flags import Flags
from tko.play.quest_visibility_service import QuestVisibilityService
from tko.play_tree.task_tree import TaskTree
from tko.game.task import Task


class GuiActionResolver:

    def __init__(self, tree: TaskTree, fman: FloatingManager, fmt_util: FormatterUtil, flags: Flags):
        self.tree = tree
        self.fman = fman
        self.fmt_util = fmt_util
        self.flags = flags

    def get_task_action(self, task: Task) -> tuple[str, str]:
        if task.resource.is_view:
            return "B", TaskAction.VISITAR
        if task.resource.is_static_type:
            return "G", TaskAction.EXECUTAR
        if not self.fmt_util.is_downloaded_for_lang(task):
            return "Y", TaskAction.BAIXAR
        return "G", TaskAction.EXECUTAR

    def get_activate_label(self) -> tuple[str, str]:
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return "R", "Retornar"
        if isinstance(obj, Quest):
            quest: Quest = obj
            if self.flags.task_view_mode.is_inbox() and not QuestVisibilityService.is_reachable(quest):
                output = TaskAction.BLOQUEIO
            elif quest.basic.full_key in self.tree.state.expanded:
                output = TaskAction.CONTRAIR
            else:
                output = TaskAction.EXPANDIR
            return "Y", output
        elif isinstance(obj, Task):
            tr = self.tree.game.get_task(obj.basic.full_key)
            color, output = self.get_task_action(tr)
            return color, output
        return "R", " ERRO"
