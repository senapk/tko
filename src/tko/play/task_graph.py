from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.settings.log_info import LogInfo
from tko.settings.logger import Logger
from tko.play.flags import Flags
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
        self.__collect()

    def __collect(self):
        logger = Logger.get_instance()
        actions = logger.tasks.key_actions.get(self.task_key, [])
        types = ["TEST", "PROG", "SELF", "FAIL"]
        filtered = [ad for ad in actions if ad.type in types]
        collected: list[float] = [0]
        last = 0
        eixo: list[float] = [0]
        count = 1
        for ad in filtered:
            if ad.coverage != -1:
                last = ad.coverage
                collected.append(last)
            else:
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
        title = self.task_key
        if self.minutes_mode:
            title += " (% / minutos)"
        else:
            title += " (% / execuções)"
        result = plot_to_string(xs=self.eixo, ys=self.collected, title=title, lines=True, y_max=101, y_min=0, width=self.width, height=self.height)
        
        if isinstance(result, str):
            return result.splitlines()
        return result
