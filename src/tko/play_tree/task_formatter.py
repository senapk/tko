from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.game.task_enums import EvalMode
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.util.rt import RT
from tko.util.symbols import Symbols


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

    def get_task_full_title(self, task: Task, key_pad: None | int, sep: str = " ", source_name: str = "") -> tuple[str, str, str]:
        basic = task.basic
        if key_pad is None:
            key_pad = len(basic.key)
        if not f"@{basic.key}" in basic.title:
            key = f"{source_name}@{basic.key}".ljust(key_pad + 1, sep) + sep
            title = basic.title
            return key + title, key, title
        return basic.title, "", basic.title

    def get_task_source_eval_symbols(self, task: Task) -> tuple[str, str]:
        """Return the compact source and evaluation codes used by the tree."""
        if not task.location.is_external:
            source_mode = "G"  # Fonte gerenciada pelo repositório.
        elif self.is_downloaded_for_lang(task):
            source_mode = Symbols.circle_filled  # Fonte externa materializada nesta linguagem.
        else:
            source_mode = Symbols.circle_void  # Fonte externa ainda imaterializada.

        eval_mode = {
            EvalMode.NONE: "N",
            EvalMode.SELF: "S",
            EvalMode.DIFF: "D",
        }[task.config.eval]
        return source_mode, eval_mode

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
