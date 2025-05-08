from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.settings.logger import Logger
from uniplot import plot_to_string # type: ignore

class TaskGraph:
    def __init__(self, settings: Settings, rep: Repository, task_key: str, width: int, height: int, minutes_mode: bool = False):
        self.settings = settings
        self.rep = rep
        self.task_key = task_key
        self.width = width
        self.height = height
        self.collected: list[float] = []
        self.eixo: list[float] = []
        self.minutes_mode = minutes_mode
        self.logger = Logger.get_instance()

    def __collect(self):
        actions = self.logger.tasks.key_actions.get(self.task_key, [])
        types = ["TEST", "PROG", "SELF", "FAIL"]
        filtered = [ad for ad in actions if ad.type in types]
        collected: list[float] = [0]
        last = 0
        eixo: list[float] = [0]
        count = 1
        for ad in filtered:
            if ad.coverage == -1 or ad.coverage == 0:
                collected.append(last)
            else:
                last = ad.coverage
                collected.append(last)
            if self.minutes_mode:
                eixo.append(ad.elapsed.total_seconds() / 60)
            else:
                eixo.append(count)
                count += 1
        self.collected = collected
        self.eixo = eixo
        # self.eixo = list(range(len(collected)))

    def get_graph(self) -> list[str]:
        lines: list[str] = self.logger.cache.get_task_cache(self.task_key)
        if len(lines) > 0:
            return lines
        self.__collect()

        title = self.task_key
        if self.minutes_mode:
            title += " (% / minutos)"
        else:
            title += " (% / execuções)"
        result = plot_to_string(xs=self.eixo, ys=self.collected, title=title, lines=True, y_max=101, y_min=0, width=self.width, height=self.height)
        
        if isinstance(result, str):
            return result.splitlines()
        return result
