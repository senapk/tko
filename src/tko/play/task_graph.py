from tko.settings.settings import Settings
from tko.settings.repository import Repository
from uniplot import plot_to_string # type: ignore
from tko.util.text import Text
from tko.logger.log_sort import LogSort
from tko.logger.log_item_exec import LogItemExec
from tko.logger.delta import Delta

class TaskGraph:
    def __init__(self, settings: Settings, rep: Repository, task_key: str, width: int, height: int):
        self.settings = settings
        self.rep = rep
        self.task_key = task_key
        self.width = width
        self.height = height
        
        self.collected_rate: list[float] = []
        self.collected_elapsed: list[float] = []
        self.collected_lines: list[float] = []

        self.total_elapsed: float = 0.0
        self.max_lines: float = 0
        self.actual_rate: float = 0.0
        
        self.eixo: list[float] = []
        self.logger = rep.logger

    def __collect(self):
        key_dict: dict[str, LogSort] = self.logger.tasks.task_dict
        if not self.task_key in key_dict:
            return
        
        item_exec_list: list[tuple[Delta, LogItemExec]] = key_dict[self.task_key].exec_list
        collected_rate: list[float] = [0]
        collected_elapsed: list[float] = [0]
        collected_lines: list[float] = [0]
        last = 0
        eixo: list[float] = [0]
        count = 1
        last_size = 0
        for delta, item in item_exec_list:
            if item.rate == -1:
                collected_rate.append(last)
            else:
                last = item.rate
                collected_rate.append(last)
            collected_elapsed.append(delta.accumulated.total_seconds())  # Convert to minutes
            if item.size > 0:
                last_size = item.size
            collected_lines.append(last_size)
            eixo.append(count)
            count += 1
        self.total_elapsed = collected_elapsed[-1]
        self.max_lines = max(collected_lines)
        self.actual_rate = collected_rate[-1] if collected_rate else 0
        if collected_elapsed[-1] != 0:
            for i in range(len(collected_elapsed)):
                collected_elapsed[i] = collected_elapsed[i] / self.total_elapsed * 100
        if self.max_lines != 0:
            for i in range(len(collected_lines)):
                collected_lines[i] = (collected_lines[i] / self.max_lines) * 100
                if collected_lines[i] < 1:
                    collected_lines[i] = 0

        self.collected_rate = collected_rate
        self.collected_elapsed = collected_elapsed
        self.collected_lines = collected_lines
        self.eixo = eixo
        # self.eixo = list(range(len(collected)))

    def get_graph(self) -> list[Text]:
        self.__collect()
        if not self.eixo:
            return []
        title = Text.format(" {C}", f" @{self.task_key} ")
        title += Text.format(" {G}", f" Total {self.actual_rate:.0f}% ")
        time_h: int = int(self.total_elapsed) // 3600
        time_m: int = (int(self.total_elapsed) % 3600) // 60
        time = f"{time_h:02.0f}h {time_m:.0f}min" if time_h > 0 else f"{time_m:.0f}min"
        title += Text.format(" {B}", f" Tempo {time} ")
        title += Text.format(" {M}", f" Linhas {self.max_lines:.0f} ")
        # if len(self.collected_elapsed) > 1:
        result = plot_to_string(xs=[self.eixo, self.eixo, self.eixo], ys=[self.collected_elapsed, self.collected_lines, self.collected_rate], lines=[True, True, True], y_min=0, y_max=101, width=self.width, height=self.height, y_unit="%", x_unit="runs")

        if isinstance(result, str):
            result = result.splitlines()

        lines: list[Text] = []
        for line in result:
            lines.append(Text.decode_raw(line))
        title = title.center(self.width)
        lines.append(title)
        return lines
        # return []