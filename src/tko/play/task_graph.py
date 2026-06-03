from tko.config.settings import Settings
from tko.repository.repository import Repository
from uniplot import plot_to_string # type: ignore
from tko.util.rt import RT, RBuffer
from tko.logger.log_sort import LogSort
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_base import LogItemBase

from tko.logger.delta import Delta

class TaskGraph:
    def __init__(self, settings: Settings, repo: Repository, task_key: str, width: int, height: int):
        self.settings = settings
        self.repo = repo
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
        self.logger = repo.logger
        self.versions = 0

        self.log_sort: LogSort | None = None
        if task_key in self.logger.tasks.task_dict:
            self.log_sort = self.logger.tasks.task_dict[task_key]

        self.raw_text: list[RT] = self.prepare_xray()

        if self.log_sort is None:
            return
        diff_list = self.log_sort.diff_list
        exec_list = self.log_sort.exec_list
        self.versions = len(diff_list)
       
        item_exec_list: list[tuple[Delta, LogItemExec]] = exec_list
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
        if not self.repo.flags.task_graph_mode.is_time_view():
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

    def prepare_xray(self) -> list[RT]:
        if self.log_sort is None:
            return []
        output: list[RT] = []
        all_entries: list[tuple[Delta, LogItemBase]] = self.log_sort.delta_list.base_list
        for delta, item in all_entries:
            data = str(item)
            data = data.split(", ")
            data = [x for x in data if not x.startswith("k:") and not x.startswith("v:")]
            data_str = ", ".join(data)
            data_str = data_str.replace("mode:", "")
            text = (RT(data_str)
                        .replace("EXEC", RT("EXEC", "g"))
                        .replace("SELF", RT("SELF", "r"))
                        .replace("MOVE", RT("MOVE", "y")))
            acc = delta.accumulated.total_seconds() / 60
            acc_h = int(acc) // 60
            acc_m = int(acc) % 60
            acc_s = int((acc - int(acc)) * 60)
            acc_str = f"{acc_h:02d}:{acc_m:02d}:{acc_s:02d}"
            output.append(RT(f"acc:{acc_str}, ") + text)
        return output

    def get_graph(self) -> list[RT]:
        x_fix = 3
        y_fix = 2
        if self.repo.flags.task_graph_mode.is_time_view():
            result = plot_to_string( # type: ignore
                color=["magenta", "green", "red"],
                xs=[self.collected_elapsed, self.collected_elapsed, self.collected_elapsed],
                ys=[self.collected_lines_len, self.collected_rate, self.collected_rate],
                lines=[True, True, False], 
                y_min=0,
                y_max=101,
                width=self.width + x_fix,
                height=self.height + y_fix,
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
                width=self.width + x_fix, 
                height=self.height + y_fix, 
                y_unit="%", 
                x_unit="runs"
            )
        
        if isinstance(result, str):
            result = result.splitlines()
        output: list[RT] = []
        for line in result:
            output.append(RT.decode_raw(line))
        fixed: list[RT] = []
        size = len(output)
        for i, line in enumerate(output):
            if i == 0 or i == size - 2:
                continue
            if i < size - 2:
                fixed.append(line.slice(2))
            else:
                fixed.append(line)
            
        return fixed

    # returns header and graph lines
    def get_output(self) -> tuple[list[RT], list[RT]]:
        if not self.eixo:
            return [], []
        
        # title = RT(f" {self.task_key} ", "C")
        title_builder = RBuffer().add(f" Total {self.actual_rate:.0f}% ", "g")
        time_h: int = int(self.total_elapsed) // 60
        time_m: int = (int(self.total_elapsed) % 60)
        time = f"{time_h:02.0f}h {time_m:.0f}min" if time_h > 0 else f"{time_m:.0f}min"
        title_builder.add(f"Tempo {time} ", "b")
        title_builder.add(f"Linhas {self.max_lines:.0f} ", "m")
        title_builder.add(f"Versões {self.versions} ", "r")
        title = title_builder.to_rt()

        header: list[RT] = []
        # title = title.center(self.width)
        
        if self.repo.flags.panel.is_graph():
            header.append(title)
            return header, self.get_graph()
        else:
            header.append(title)
            return header, self.raw_text
        
        
