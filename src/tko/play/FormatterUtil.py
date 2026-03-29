from tko.down.sandbox_drafts import SandboxDrafts
from tko.game.quest import Quest
from tko.game.task import Task
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.util.symbols import Symbols
from tko.util.text import Text


class FormatterUtil:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo
        self.cache_task_times: dict[str, tuple[int, int]] = {}

    def is_downloaded_for_lang(self, task: Task):
        folder = task.get_workspace_folder()
        if folder is None:
            return False

        lang = self.repo.data.lang
        drafts = SandboxDrafts.load_drafts_only(folder, lang)
        if drafts:
            return True
        return False

    def count_visible_hidden_tasks(self, quest: Quest) -> tuple[int, int]:
        visible = 0
        hidden = 0
        for t in quest.get_tasks():
            if not self.is_hide_tasks(t):
                visible += 1
            else:
                hidden += 1
        return visible, hidden

    def is_hide_tasks(self, task: Task) -> bool:
        if self.repo.flags.task_view_mode.is_inbox() and task.task_path == Task.TaskPath.SIDE and not self.is_downloaded_for_lang(task):
            return True
        return False

    def get_task_down_symbol(self, t: Task) -> tuple[str, str]:
        if t.is_link():
            if t.info.feedback:
                return ("g", Symbols.task_view)
            return ("", Symbols.task_view)

        if not t.is_import_type():
            if t.info.feedback:
                return ("g", Symbols.right_triangle_filled)
            return ("", Symbols.right_triangle_void)
        if self.is_downloaded_for_lang(t):
            if t.info.feedback:
                return ("g", Symbols.down_triangle_filled)
            return ("", Symbols.down_triangle_void)
        if t.info.feedback:
            return ("g", Symbols.up_triangle_filled)
        return ("", Symbols.up_triangle_void)

    def get_task_path_symbol(self, t: Task) -> tuple[str, str]:
        if t.task_path == Task.TaskPath.MAIN:
            return ("y", Symbols.star_filled)
        return ("", Symbols.star_void)

    def get_task_help_symbol(self, t: Task) -> tuple[str, str]:
        if t.task_help == Task.TaskHelp.FREE:
            return ("g", Symbols.task_reload)
        if t.task_help == Task.TaskHelp.PART:
            return ("y", Symbols.task_reload)
        if t.task_help == Task.TaskHelp.ZERO:
            return ("r", Symbols.task_zero)
        return ("", "")

    def get_task_mode_symbol(self, t: Task) -> tuple[str, str]:
        if t.task_mode == Task.TaskMode.VIEW:
            return ("c", Symbols.task_view)
        if t.task_mode == Task.TaskMode.EDIT:
            return ("c", Symbols.task_edit)
        return ("", Symbols.task_edit)

    def format_percent_1s(self, value: float) -> Text:
        prog = value
        if prog < 0.1:
            return Text().addf("", Symbols.middle_dot)
        if prog > 99:
            return Text().addf("g", Symbols.check)
        return Text().addf("y", str(round(prog / 10)).rjust(1, "0"))

    def format_percent_2s(self, value: float | None) -> Text:
        if value is None:
            return Text().addf("", "--")
        prog = round(value)
        if prog < 0.1:
            return Text().add(Symbols.middle_dot + Symbols.middle_dot)
        if prog > 99:
            return Text().addf("g", Text() + "▬▬")

        return Text().addf("y", str(prog).rjust(2, "0"))

    def get_percent_color(self, value: float) -> str:
        color = "g" if value > 99 else ("y" if value > 49 else "r")
        return color

    def format_hours_minutes(self, color: str, hours: int, minutes: int) -> Text:
        output = Text()
        if hours > 0 or minutes > 0:
            output.addf(color, f"{hours:02}h{minutes:02}m ")
        else:
            output.add("┄" * 6 + " ")
        return output

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
    def color_task_title(title: str, color: str) -> Text:
        words = title.split(" ")
        output = Text()
        for i, word in enumerate(words):
            if word.startswith("@") or word.startswith("#") or word.startswith("!"):
                output.addf(color + "g", word)
            elif word.startswith(":"):
                output.addf(color + "y", word)
            elif word.startswith("*"):
                output.addf(color + "c", word)
            elif word.startswith("+"):
                output.addf(color + "c", word)
            else:
                output.addf(color, word)
            if i < len(words) - 1:
                output.addf(color, " ")
        return output