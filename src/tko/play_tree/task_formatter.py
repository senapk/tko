from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.game.task_enums import TaskEval
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.util.rt import RT


class TaskFormatter:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo

    def is_downloaded(self, task: Task) -> bool:
        folder = self.repo.task_resolver.target_folder(task)
        if folder is None:
            return False
        return folder.exists()

    def is_downloaded_for_lang(self, task: Task):
        folder = self.repo.task_resolver.target_folder(task)
        if folder is None:
            return False

        lang = self.repo.data.lang
        finder = DraftsFinderCached(folder, lang)
        drafts = finder.load_source_files()
        return len(drafts) > 0

    def get_task_full_title(self, task: Task, key_pad: None | int, sep: str = " ", remote_name: str = "") -> tuple[str, str, str]:
        basic = task.basic
        if key_pad is None:
            key_pad = len(basic.key)
        if not f"@{basic.key}" in basic.title:
            key = f"{remote_name}@{basic.key}".ljust(key_pad + 1, sep) + sep
            title = basic.title
            return key + title, key, title
        return basic.title, "", basic.title

    def get_task_down_test_eval_symbol(self, task: Task) -> tuple[str, str]:
        # state
        read = "R"
        static = "X" #Symbols.circle_filled
        empty = "○" #Symbols.square_void
        down = "●" #Symbols.square_filled

        # mode
        test = "T"
        selF = "S"

        
        if task.config.test == TaskEval.TEST:
            test_mode = test
        else:
            test_mode = selF

        if task.location.is_read:
            state_mode = read
        elif task.location.is_static_type:
            state_mode = static
        elif self.is_downloaded_for_lang(task):
            state_mode = down
        else:
            state_mode = empty
        
        return (state_mode, test_mode)

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