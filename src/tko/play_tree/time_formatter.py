from tko.game.quest import Quest
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.util.symbols import Symbols
from tko.util.rtext import RText


class TimeFormatter:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.cache_task_times: dict[str, tuple[int, int]] = {}

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
        if task.basic.full_key in self.cache_task_times:
            return self.cache_task_times[task.basic.full_key]
        logsort = self.repo.logger.tasks.task_dict.get(task.basic.full_key, None)
        if logsort is not None and len(logsort.base_list) > 0:
            delta, _ = logsort.base_list[-1]
            hours = delta.accumulated.seconds // 3600
            minutes = (delta.accumulated.seconds % 3600) // 60
            self.cache_task_times[task.basic.full_key] = (hours, minutes)
            return hours, minutes
        self.cache_task_times[task.basic.full_key] = (0, 0)
        return 0, 0

    def get_quest_time(self, quest: Quest) -> tuple[int, int]:
        hours = 0
        minutes = 0
        for task in quest.get_tasks():
            th, tm = self.get_task_hours_minutes(task)
            hours += th
            minutes += tm
        hours += minutes // 60
        minutes = minutes % 60
        return hours, minutes