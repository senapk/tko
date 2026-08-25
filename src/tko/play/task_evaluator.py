from tko.game.task import Task
from tko.game.feedback import Feedback
from tko.floating.floating_grade import FloatingGrade
from tko.floating.floating_manager import FloatingManager
from tko.config.settings import Settings
from tko.play.opener import Opener
from tko.play_tree.task_tree import TaskTree
from tko.repository.repository import Repository
from tko.logger.log_item_self import LogItemSelf


class TaskEvaluator:

    def __init__(self, repo: Repository, settings: Settings, fman: FloatingManager, tree: TaskTree):
        self.repo = repo
        self.settings = settings
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
            feedback = Feedback(self.repo, obj)
            feedback_path = feedback.get_feedback_toml_path()
            feedback_opener = None
            if feedback_path is not None:
                opener = Opener(self.settings).set_language(self.repo.data.lang).add_files_to_open([feedback_path])
                feedback_opener = opener.open_files
            floating = FloatingGrade(
                obj,
                lambda task: self.repo.logger.store(LogItemSelf().set_task(task)),
                feedback,
                feedback_opener,
            ).set_id("self")
            self.fman.add_floating(floating)
