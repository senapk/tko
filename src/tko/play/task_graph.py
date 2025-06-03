from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.settings.logger import Logger
from uniplot import plot_to_string # type: ignore
from tko.util.text import Text

class TaskGraph:
    def __init__(self, settings: Settings, rep: Repository, task_key: str, width: int, height: int):
        self.settings = settings
        self.rep = rep
        self.task_key = task_key
        self.width = width
        self.height = height
        self.collected_cov: list[float] = []
        self.collected_elapsed: list[float] = []
        self.total_elapsed: float = 0.0
        self.max_lines: float = 0
        self.eixo: list[float] = []
        self.logger = Logger.get_instance()

    def __collect(self):
        actions = self.logger.tasks.key_actions.get(self.task_key, [])
        types = ["TEST", "PROG", "SELF", "FAIL"]
        filtered = [ad for ad in actions if ad.type in types]
        collected_cov: list[float] = [0]
        collected_elapsed: list[float] = [0]
        collected_lines: list[float] = [0]
        last = 0
        eixo: list[float] = [0]
        count = 1
        for ad in filtered:
            if ad.coverage == -1 or ad.coverage == 0:
                collected_cov.append(last)
            else:
                last = ad.coverage
                collected_cov.append(last)
            collected_elapsed.append(ad.elapsed.total_seconds() / 60)
            collected_lines.append(ad.lines)
            # if self.minutes_mode:
            #     eixo.append(ad.elapsed.total_seconds() / 60)
            # else:
            eixo.append(count)
            count += 1
        self.total_elapsed = collected_elapsed[-1]
        self.max_lines = max(collected_lines)
        if collected_elapsed[-1] != 0:
            for i in range(len(collected_elapsed)):
                collected_elapsed[i] = collected_elapsed[i] / self.total_elapsed * 100
        if self.max_lines != 0:
            for i in range(len(collected_lines)):
                collected_lines[i] = (collected_lines[i] / self.max_lines) * 100
                if collected_lines[i] < 1:
                    collected_lines[i] = 0

        self.collected_cov = collected_cov
        self.collected_elapsed = collected_elapsed
        self.collected_lines = collected_lines
        self.eixo = eixo
        # self.eixo = list(range(len(collected)))

    def get_graph(self) -> list[Text]:
        self.__collect()
        lines: list[Text] = []
        title = Text.format(" {C}", f" @{self.task_key} ")
        title += Text.format(" {B}", f" Tempo: {self.total_elapsed:.0f} min ")
        title += Text.format(" {G}", f" Total: {self.collected_cov[-1]:.0f} % ")
        title += Text.format(" {M}", f" Linhas: {self.max_lines:.0f} ")
        # if len(self.collected_elapsed) > 1:
        result = plot_to_string(xs=[self.eixo, self.eixo, self.eixo], ys=[self.collected_elapsed, self.collected_lines, self.collected_cov], lines=True, y_min=0, width=self.width, height=self.height)

        if isinstance(result, str):
            result = result.splitlines()

        for line in result:
            lines.append(Text.decode_raw(line))
        title = title.center(self.width)
        lines.append(title)
        return lines
        # return []