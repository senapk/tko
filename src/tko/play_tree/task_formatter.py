from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.game.task import Task
from tko.game.task_config import TaskLoss, TaskMain, TaskTest
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.util.symbols import Symbols
from tko.util.rt import RT


class TaskFormatter:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo

    def is_downloaded(self, task: Task) -> bool:
        try:
            folder = task.path.work_dir
        except Exception as _:
            return False
        if folder is None:
            return False
        return folder.exists()

    def is_downloaded_for_lang(self, task: Task):
        try:
            folder = task.path.work_dir
        except Exception as _:
            return False
        if folder is None:
            return False

        lang = self.repo.data.lang
        finder = DraftsFinderCached(folder, lang)
        drafts = finder.load_source_files()
        return len(drafts) > 0

    def get_task_full_title(self, task: Task, key_pad: None | int, pad_char: str = " ", remote_name: str = "") -> tuple[str, str, str]:
        basic = task.basic
        if key_pad is None:
            key_pad = len(basic.key)
        if not f"@{basic.key}" in basic.title:
            key = f"{remote_name}@{basic.key}".ljust(key_pad, pad_char) + " "
            title = basic.title
            return key + title, key, title
        return basic.title, "", basic.title

    def get_task_down_symbol(self, task: Task) -> tuple[str, str]:
        if task.resource.is_view:
            if task.info.feedback:
                return ("g", Symbols.task_view)
            return ("", Symbols.task_view)
        if task.config.test == TaskTest.TEST:
            if self.is_downloaded_for_lang(task):
                if task.info.feedback:
                    return ("g", Symbols.diamond_filled)   # baixou e tem feedback
                return ("", Symbols.diamond_filled)        # baixou e não tem feedback
            elif self.is_downloaded(task):
                if task.info.feedback:
                    return ("r", Symbols.diamond_void)   # baixou e tem feedback
                return ("y", Symbols.diamond_void)        # baixou e não tem feedback
            else:
                if task.info.feedback:
                    return ("r", Symbols.diamond_void)       # não baixou e tem feedback
                return ("", Symbols.diamond_void)              # não baixou e não tem feedback
        elif task.config.test == TaskTest.SELF:
            if self.is_downloaded_for_lang(task):
                if task.info.feedback:
                    return ("g", Symbols.square_filled)   # baixou e tem feedback
                return ("", Symbols.square_filled)        # baixou e não tem feedback
            elif self.is_downloaded(task):
                if task.info.feedback:
                    return ("r", Symbols.square_void)   # baixou e tem feedback
                return ("y", Symbols.square_void)        # baixou e não tem feedback
            else:
                if task.info.feedback:
                    return ("r", Symbols.square_void)       # não baixou e tem feedback
                return ("", Symbols.square_void)              # não baixou e não tem feedback
        return ("x", "x")

    def get_task_path_symbol(self, task: Task) -> tuple[str, str]:
        color = "y" if task.resource.is_import_type else "m"
        if task.config.path == TaskMain.MAIN:
            return (color, Symbols.star_filled)
        return (color, Symbols.star_void)

    def get_task_help_symbol(self, task: Task) -> tuple[str, str]:
        if task.config.loss == TaskLoss.FREE:
            return ("g", Symbols.loss_free)
        if task.config.loss == TaskLoss.PART:
            return ("y", Symbols.loss_part)
        if task.config.loss == TaskLoss.ZERO:
            return ("r", Symbols.loss_zero)
        return ("", "")

    @staticmethod
    def color_task_title(key: str, title: str) -> RT:
        words = title.split(" ")
        output = RT()
        for i, word in enumerate(words):
            if word.startswith("@") or word.startswith("#") or word.startswith("!"):
                output += RT(word, "g")
            elif word.startswith(":"):
                output += RT(word, "y")
            elif word.startswith("*"):
                output += RT(word, "c")
            elif word.startswith("+"):
                output += RT(word, "c")
            else:
                output += word
            if i < len(words) - 1:
                output += " "
        if key != "":
            output = RT(key, "g") + output
        return output