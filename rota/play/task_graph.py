from rota.settings.settings import Settings
from rota.settings.repository import Repository
from rota.util.logger import ActionData, LogAction
from uniplot import plot_to_string # type: ignore

class TaskGraph:
    def __init__(self, settings: Settings, rep: Repository, task_key: str, width: int, height: int):
        self.settings = settings
        self.rep = rep
        self.task_key = task_key
        self.width = width
        self.height = height
        history = self.rep.get_history_file()
        with open(history, "r") as f:
            content = f.read()
        actions: list[ActionData] = ActionData.parse_history_file(content)
        filtered = [ad for ad in actions if ad.task_key == task_key]
        filtered = [ad for ad in filtered if ad.action_value == LogAction.TEST.value or ad.action_value == LogAction.PROG.value]
        collected: list[int] = [0]
        last = 0
        for ad in filtered:
            try:
                last = int(ad.payload)
                collected.append(last)
            except:
                collected.append(last)
        self.collected = collected

    def get_collected(self) -> list[int]:
        return self.collected
    
    def get_graph(self) -> list[str]:
        collected = self.get_collected()
        result = plot_to_string(collected, title=self.task_key, lines=True, y_max=101, y_min=0, width=self.width, height=self.height)
        return result
