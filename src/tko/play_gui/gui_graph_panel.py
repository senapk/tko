from tko.collect.task_collected import TaskCollected
from tko.config.flags import Flags
from tko.config.settings import Settings
from tko.game.quest import Quest
from tko.play.daily_graph import DailyGraph
from tko.play.task_graph import TaskGraph
from tko.repository.repository import Repository
from tko.util.rt import RT


class GuiGraphPanel:
    """Graph and history data provider for Textual widgets."""

    def __init__(self, settings: Settings, repo: Repository, flags: Flags):
        self.settings = settings
        self.repo = repo
        self.flags = flags

    def get_task_graph(self, task_key: str, width: int, height: int) -> tuple[bool, list[RT], list[RT]]:
        header, graph = TaskGraph(self.settings, self.repo, task_key, width, height).get_output()
        return bool(graph), header, graph

    def get_history(self, quest: Quest | None = None) -> tuple[bool, list[RT], list[RT]]:
        remote_paths = {source.name: source.path_or_url for source in self.repo.sources.values()}
        task_keys: set[str] | None = None if quest is None else {task.basic.full_key for task in quest.get_tasks()}
        history: list[TaskCollected] = self.repo.logger.tasks.mount_task_history(self.repo.game, remote_paths, task_keys)
        task_pad = max((len(item.key) for item in history), default=0) + 2
        quest_pad = max((len(item.quest) for item in history), default=0) + 2
        rows: list[RT] = []
        for item in history:
            item.resume.events = 0
            values = item.get_kv(include_key=False, include_quest=False)
            del values["remote"]
            values["duration"] = f"{values['duration']:<5.2f}"
            text = str(values).replace("'", "").replace("{", "").replace("}", "")
            text = text.replace("grader: ", "").replace(", init: ", "%, ").replace("duration: ", "")
            rows.append(RT.parse(f"[g]{item.key:<{task_pad}}[.] {item.quest:<{quest_pad}} {text}"))
        return True, [RT.parse(" [r]History ")], rows

    def get_daily_graph(self, width: int, height: int) -> tuple[bool, list[RT], list[RT]]:
        header, graph = DailyGraph(self.repo.logger, width, height).get_graph()
        return bool(graph), header, graph
