from tko.game.quest import Quest
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.util.rtext import RText
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.quest_formatter import QuestFormatter
from tko.play_tree.time_formatter import TimeFormatter


class FormatterUtil:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo
        self.task_formatter = TaskFormatter(settings, repo)
        self.time_formatter = TimeFormatter(repo)
        self.quest_formatter = QuestFormatter(settings, self.time_formatter)


    def is_downloaded(self, task: Task) -> bool:
        return self.task_formatter.is_downloaded(task)

    def is_downloaded_for_lang(self, task: Task):
        return self.task_formatter.is_downloaded_for_lang(task)

    def count_visible_hidden_tasks(self, quest: Quest) -> tuple[int, int]:
        return self.quest_formatter.count_visible_hidden_tasks(quest)

    def get_start_symbols_and_percent_text(self, q: Quest) -> tuple[str, RText]:
        return self.quest_formatter.get_start_symbols_and_percent_text(q)

    def get_quest_full_title(self, quest: Quest, show_skills: bool) -> RText:
        return self.quest_formatter.get_quest_full_title(quest, show_skills)


    def get_task_full_title(self, task: Task, key_pad: None | int, pad_char: str = " ", remote_name: str = "") -> tuple[str, str, str]:
        return self.task_formatter.get_task_full_title(task, key_pad, pad_char, remote_name)

    def get_task_down_symbol(self, task: Task) -> tuple[str, str]:
        return self.task_formatter.get_task_down_symbol(task)


    def get_task_path_symbol(self, task: Task) -> tuple[str, str]:
        return self.task_formatter.get_task_path_symbol(task)


    def get_task_help_symbol(self, task: Task) -> tuple[str, str]:
        return self.task_formatter.get_task_help_symbol(task)

    def format_percent_1s(self, value: float) -> RText:
        return self.time_formatter.format_percent_1s(value)

    def format_percent_2s(self, value: float | None) -> RText:
        return self.time_formatter.format_percent_2s(value)

    def format_percent_3s(self, value: float | None) -> RText:
        return self.time_formatter.format_percent_3s(value)

    def get_percent_color(self, value: float) -> str:
        return self.time_formatter.get_percent_color(value)

    def format_hours_minutes(self, color: str, hours: int, minutes: int) -> RText:
        return self.time_formatter.format_hours_minutes(color, hours, minutes)

    def get_task_hours_minutes(self, task: Task) -> tuple[int, int]:
        return self.time_formatter.get_task_hours_minutes(task)

    def get_quest_time(self, quest: Quest) -> tuple[int, int]:
        return self.time_formatter.get_quest_time(quest)

    def get_focus_color_quest(self, item: Quest) -> str:
        return self.quest_formatter.get_focus_color_quest(item)

    @staticmethod
    def color_task_title(key: str, title: str) -> RText:
        return TaskFormatter.color_task_title(key, title)
