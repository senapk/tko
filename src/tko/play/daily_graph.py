from tko.logger.logger import Logger
from tko.util.rt import RT
from tko.logger.delta import Delta
from tko.widget.terminal_chart import Series, TerminalChart

class DailyGraph:
    def __init__(self, logger: Logger, width: int, height: int):
        self.logger = logger
        self.width = width
        self.height = height
        self.daily: list[float] = []
        self.accumulates: list[float] = []
        self.eixo: list[float] = []
        # self.raw_text: list[str] = []
        self.__collect()

    def __collect(self):
        days_info = self.logger.daily.resume()
        sorted_keys = sorted(days_info.keys())
        
        self.daily = [0]
        self.accumulates = [0]
        for item in sorted_keys:
            self.daily.append(days_info[item].elapsed_seconds)
            self.accumulates.append(self.accumulates[-1] + days_info[item].elapsed_seconds)
        
        for i, value in enumerate(self.daily):
            self.daily[i] = value / 3600
        for i, value in enumerate(self.accumulates):
            self.accumulates[i] = value / 3600

        self.eixo = list(range(len(self.daily)))

    # def get_collected(self) -> list[str]:
    #     output: list[str] = []
    #     for value in self.collected:
    #         output.append(f"{value:.2f}")
    #     for i in range(len(output)):
    #         output[i] = output[i].replace(".", ":").rjust(5, " ")
    #     return output

    def get_graph(self) -> tuple[list[RT], list[RT]]:
        # collected: list[float] = []
        # eixo: list[int] = []
        if not self.daily:
            return [], []

        daily: list[float] = [x for x in self.daily]
        accumulates: list[float] = [x for x in self.accumulates]

        max_daily = max(daily) if daily else 0
        max_accumulates = max(accumulates) if accumulates else 0

        for i in range(len(daily)):
            daily[i] = daily[i] / max_daily * 100 if max_daily > 0 else 0
            accumulates[i] = accumulates[i] / max_accumulates * 100 if max_accumulates > 0 else 0

        eixo: list[float] = []
        bar: list[float] = []
        day = 1
        for value in daily:
            eixo.append(day)
            bar.append(0)
            eixo.append(day)
            bar.append(value)
            eixo.append(day)
            bar.append(0)
            day += 1

        eixo = [x / 7 for x in eixo]
        accumulated_axis = [x / 7 for x in self.eixo]
        fixed = TerminalChart(
            self.width,
            self.height,
            [Series(list(zip(eixo, bar)), "c"), Series(list(zip(accumulated_axis, accumulates)), "m")],
            y_min=0,
            y_max=100,
        ).render()


        
        header = [
            RT(" Máximo diário: ", "c")
            + RT(f"{Delta.format_h_min(max_daily)} ", "c")
            + " "
            + RT(" Acumulado: ", "m")
            + RT(f"{Delta.format_h_min(max_accumulates)} ", "m")
        ]
        

        return header, fixed
