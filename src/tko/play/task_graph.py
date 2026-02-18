from tko.settings.settings import Settings
from tko.settings.repository import Repository
from uniplot import plot_to_string # type: ignore
from tko.util.text import Text
from tko.logger.log_sort import LogSort
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_base import LogItemBase
from tko.util.miniwi import Miniwi
from tko.logger.delta import Delta
from tko.play.flags import Flags

class TaskGraph:
    def __init__(self, settings: Settings, rep: Repository, task_key: str, width: int, height: int):
        self.settings = settings
        self.rep = rep
        self.task_key = task_key
        self.width = width
        self.height = height - 1
        
        self.collected_rate: list[float] = []
        self.collected_elapsed: list[float] = []
        self.collected_lines_len: list[float] = []

        self.total_elapsed: float = 0.0
        self.max_lines: float = 0
        self.actual_rate: float = 0.0
        
        self.eixo: list[float] = []
        self.logger = rep.logger
        self.versions = 0

        self.log_sort: LogSort | None = None
        if task_key in self.logger.tasks.task_dict:
            self.log_sort = self.logger.tasks.task_dict[task_key]

        self.raw_text: list[Text] = self.prepare_xray()

        if self.log_sort is None:
            return
        self.versions = len(self.log_sort.diff_list)
       
        item_exec_list: list[tuple[Delta, LogItemExec]] = self.log_sort.exec_list
        collected_rate: list[float] = [0]
        collected_elapsed: list[float] = [0]
        collected_lines_len: list[float] = [0]
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
            collected_elapsed.append(delta.accumulated.total_seconds() / 60)  # Convert to minutes
            if item.size > 0:
                last_size = item.size
            collected_lines_len.append(last_size)
            eixo.append(count)
            count += 1
        self.actual_rate = collected_rate[-1] if collected_rate else 0

        self.total_elapsed = collected_elapsed[-1]
        # normalizando tempo para porcentagem
        if not Flags.task_graph.get_value() == Flags.task_time_view:
            if collected_elapsed[-1] != 0:
                for i in range(len(collected_elapsed)):
                    collected_elapsed[i] = collected_elapsed[i] / self.total_elapsed * 100

        # normalizando linhas para porcentagem        
        self.max_lines = max(collected_lines_len)
        if self.max_lines != 0:
            for i in range(len(collected_lines_len)):
                collected_lines_len[i] = (collected_lines_len[i] / self.max_lines) * 100
                if collected_lines_len[i] < 1:
                    collected_lines_len[i] = 0

        self.collected_rate = collected_rate
        self.collected_elapsed = collected_elapsed
        self.collected_lines_len = collected_lines_len
        self.eixo = eixo
        # self.eixo = list(range(len(collected)))

    def prepare_xray(self) -> list[Text]:
        if self.log_sort is None:
            return []
        output: list[Text] = []
        all_entries: list[tuple[Delta, LogItemBase]] = self.log_sort.base_list
        for delta, item in all_entries:
            data = str(item)
            data = data.split(", ")
            data = [x for x in data if not x.startswith("k:") and not x.startswith("v:")]
            data_str = ", ".join(data)
            data_str = data_str.replace("mode:", "")
            text = (Text().add(data_str)
                        .replace("EXEC", Text.Token("EXEC", "g"))
                        .replace("SELF", Text.Token("SELF", "r"))
                        .replace("MOVE", Text.Token("MOVE", "y")))
            acc = delta.accumulated.total_seconds() / 60
            acc_h = int(acc) // 60
            acc_m = int(acc) % 60
            acc_s = int((acc - int(acc)) * 60)
            acc_str = f"{acc_h:02d}:{acc_m:02d}:{acc_s:02d}"
            output.append(Text().add(f"acc:{acc_str}, ").add(text))
        return output

    def get_graph(self) -> list[Text]:
        if Flags.task_graph.get_value() == Flags.task_time_view:
            result = plot_to_string(
                color=["magenta", "green", "red"],
                xs=[self.collected_elapsed, self.collected_elapsed, self.collected_elapsed],
                ys=[self.collected_lines_len, self.collected_rate, self.collected_rate],
                lines=[True, True, False], 
                y_min=0,
                y_max=101,
                width=self.width,
                height=self.height,
                y_unit="%",
                x_unit="min"
            )
        else:
            result = plot_to_string(
                color=["magenta", "green", "blue", "red"], 
                xs=[self.eixo, self.eixo, self.eixo, self.eixo], 
                ys=[self.collected_lines_len, self.collected_rate, self.collected_elapsed, self.collected_rate], 
                lines=[True, True, True, False], 
                y_min=0, 
                y_max=101, 
                width=self.width, 
                height=self.height, 
                y_unit="%", 
                x_unit="runs"
            )
        
        if isinstance(result, str):
            result = result.splitlines()
        output: list[Text] = []
        for line in result:
            output.append(Text.decode_raw(line))
        return output

    # returns header and graph lines
    def get_output(self) -> tuple[list[Text], list[Text]]:
        if not self.eixo:
            return [], []
        
        tag = Miniwi.render_dotted(self.task_key)
        first, second = tag.splitlines()
        
        # title = Text.format(" {C}", f" {self.task_key} ")
        title = Text()
        title += Text.format(" {G}", f" Total {self.actual_rate:.0f}% ")
        time_h: int = int(self.total_elapsed) // 60
        time_m: int = (int(self.total_elapsed) % 60)
        time = f"{time_h:02.0f}h {time_m:.0f}min" if time_h > 0 else f"{time_m:.0f}min"
        title += Text.format(" {B}", f" Tempo {time} ")
        title += Text.format(" {M}", f" Linhas {self.max_lines:.0f} ")
        title += Text.format(" {R}", f" Versões {self.versions} ")

        header: list[Text] = []
        # title = title.center(self.width)
        header.append(Text().add(first) + title.center(self.width - len(first)))
        
        if Flags.graph.get_value() == Flags.graph_logs:
            header.append(Text().addf("", second) + Text.format(" {C} {M}", " Scroll Up [PageUp] ", " Scroll Down [PgDown] ").center(self.width - len(second)))
            return header, self.raw_text
        
        if Flags.task_graph.get_value() == Flags.task_time_view:
            exec_color = "Y"
            time_color = "G"
        else:
            exec_color = "G"
            time_color = "Y"
        header.append(Text().addf("", second) + Text.format(f" {{{exec_color}}} {{{time_color}}}", " ExecGraph [PageUp] ",  " TimeGraph [PageDown] ").center(self.width - len(second)))
        return header, self.get_graph()
        