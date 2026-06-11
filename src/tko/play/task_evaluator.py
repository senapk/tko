from tko.game.task import Task
from tko.floating.floating_grade import FloatingGrade
from tko.floating.floating_manager import FloatingManager
from tko.play_tree.task_tree import TaskTree
from tko.repository.repository import Repository
from tko.logger.log_item_self import LogItemSelf


class TaskEvaluator:

    def __init__(self, repo: Repository, fman: FloatingManager, tree: TaskTree):
        self.repo = repo
        self.fman = fman
        self.tree = tree

    def register_action(self, task: Task):
        self.repo.logger.store(LogItemSelf().set_task(task))

    def self_evaluate_full(self):
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return
        if isinstance(obj, Task):
            task: Task = obj
            if not task.info.feedback:
                task.info.rate = 100
                task.info.feedback = True
            else:
                task.info.rate = 0
                task.info.feedback = False
            self.repo.logger.store(LogItemSelf().set_task(task))

    def self_evaluate(self):
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return
        if isinstance(obj, Task):
            obj = FloatingGrade(obj, lambda task: self.repo.logger.store(LogItemSelf().set_task(task)))
            obj.id = "self"
            self.fman.add_input(obj)
