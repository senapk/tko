from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.task_config import TaskEdit, TaskLoss, TaskMain, TaskTest
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.util.symbols import Symbols
from tko.util.rtext import RText


class FormatterUtil:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo
        self.cache_task_times: dict[str, tuple[int, int]] = {}


    def is_downloaded(self, task: Task):
        folder = task.get_workspace_folder()
        if folder is None:
            return False
        return folder.exists()

    def is_downloaded_for_lang(self, task: Task):
        folder = task.get_workspace_folder()
        if folder is None:
            return False

        lang = self.repo.data.lang
        finder = DraftsFinderCached(folder, lang)
        drafts = finder.load_source_files()
        return len(drafts) > 0

    def count_visible_hidden_tasks(self, quest: Quest) -> tuple[int, int]:
        visible = 0
        hidden = 0
        for t in quest.get_tasks():
            if t.visible:
                visible += 1
            else:
                hidden += 1
        return visible, hidden

    def get_start_symbols_and_percent_text(self, q: Quest) -> tuple[str, RText]:
        symbol = ""
        pmain, pall = q.get_percent_main_and_all()
        if pmain is not None:
            percent_text = self.format_percent_3s(pall).set_style("g")
            symbol = Symbols.star_filled
        else:
            percent_text = self.format_percent_3s(pall).set_style("g")
            symbol = Symbols.star_void
        return symbol, percent_text

    def get_task_down_symbol(self, t: Task) -> tuple[str, str]:
        if t.config.mode == TaskEdit.VIEW:
            if t.info.feedback:
                return ("g", Symbols.task_view)
            return ("", Symbols.task_view)
        if t.config.test == TaskTest.TEST:
            if self.is_downloaded_for_lang(t):
                if t.info.feedback:
                    return ("g", Symbols.diamond_filled)   # baixou e tem feedback
                return ("", Symbols.diamond_filled)        # baixou e não tem feedback
            elif self.is_downloaded(t):
                if t.info.feedback:
                    return ("r", Symbols.diamond_void)   # baixou e tem feedback
                return ("y", Symbols.diamond_void)        # baixou e não tem feedback
            else:
                if t.info.feedback:
                    return ("r", Symbols.diamond_void)       # não baixou e tem feedback
                return ("", Symbols.diamond_void)              # não baixou e não tem feedback
        elif t.config.test == TaskTest.SELF:
            if self.is_downloaded_for_lang(t):
                if t.info.feedback:
                    return ("g", Symbols.square_filled)   # baixou e tem feedback
                return ("", Symbols.square_filled)        # baixou e não tem feedback
            elif self.is_downloaded(t):
                if t.info.feedback:
                    return ("r", Symbols.square_void)   # baixou e tem feedback
                return ("y", Symbols.square_void)        # baixou e não tem feedback
            else:
                if t.info.feedback:
                    return ("r", Symbols.square_void)       # não baixou e tem feedback
                return ("", Symbols.square_void)              # não baixou e não tem feedback
        return ("x", "x")


    def get_task_path_symbol(self, t: Task) -> tuple[str, str]:
        color = "y" if t.is_import_type() else "m"
        if t.config.path == TaskMain.MAIN:
            return (color, Symbols.star_filled)
        return (color, Symbols.star_void)


    def get_task_help_symbol(self, t: Task) -> tuple[str, str]:
        if t.config.loss == TaskLoss.FREE:
            return ("g", Symbols.loss_free)
        if t.config.loss == TaskLoss.PART:
            return ("y", Symbols.loss_part)
        if t.config.loss == TaskLoss.ZERO:
            return ("r", Symbols.loss_zero)
        return ("", "")

    def format_percent_1s(self, value: float) -> RText:
        prog = value
        if prog < 0.1:
            return RText(Symbols.middle_dot)
        if prog > 99:
            return RText(Symbols.check, "g")
        return RText(str(round(prog / 10)).rjust(1, "0"), "y")

    def format_percent_2s(self, value: float | None) -> RText:
        if value is None:
            return RText("--")
        prog = round(value)
        if prog < 0.1:
            return RText(Symbols.middle_dot + Symbols.middle_dot)
        if prog > 99:
            return RText("▬▬", "g")

        return RText(str(prog).rjust(2, "0"), "y")

    def format_percent_3s(self, value: float | None) -> RText:
        if value is None or value < 1:
            return RText("----")
        rvalue = round(value)
        color = self.get_percent_color(value)
        return RText(f"{rvalue:>3}%", color)

    def get_percent_color(self, value: float) -> str:
        color = "g" if value > 99 else ("y" if value > 49 else "r")
        return color

    def format_hours_minutes(self, color: str, hours: int, minutes: int) -> RText:
        if hours > 0 or minutes > 0:
            return RText(f"{hours:02}h{minutes:02}m ", color)
        return RText("------ ")

    def get_task_hours_minutes(self, task: Task) -> tuple[int, int]:
        if task.get_full_key() in self.cache_task_times:
            return self.cache_task_times[task.get_full_key()]
        logsort = self.repo.logger.tasks.task_dict.get(task.get_full_key(), None)
        if logsort is not None and len(logsort.base_list) > 0:
            delta, _ = logsort.base_list[-1]
            hours = delta.accumulated.seconds // 3600
            minutes = (delta.accumulated.seconds % 3600) // 60
            self.cache_task_times[task.get_full_key()] = (hours, minutes)
            return hours, minutes
        self.cache_task_times[task.get_full_key()] = (0, 0)
        return 0, 0

    def get_quest_time(self, quest: Quest) -> tuple[int, int]:
        hours = 0
        minutes = 0
        for t in quest.get_tasks():
            th, tm = self.get_task_hours_minutes(t)
            hours += th
            minutes += tm
        hours += minutes // 60
        minutes = minutes % 60
        return hours, minutes

    def get_focus_color_quest(self, item: Quest) -> str:
        if not item.is_reachable():
                return "R"
        return self.settings.colors.focused_item

    @staticmethod
    def color_task_title(key: str, title: str) -> RText:
        words = title.split(" ")
        output = RText()
        for i, word in enumerate(words):
            if word.startswith("@") or word.startswith("#") or word.startswith("!"):
                output += RText(word, "g")
            elif word.startswith(":"):
                output += RText(word, "y")
            elif word.startswith("*"):
                output += RText(word, "c")
            elif word.startswith("+"):
                output += RText(word, "c")
            else:
                output += word
            if i < len(words) - 1:
                output += " "
        if key != "":
            output = RText(key, "g") + output
        return output
