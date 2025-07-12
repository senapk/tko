from tko.logger.logger import Logger
from uniplot import plot_to_string
from tko.util.text import Text
from tko.logger.delta import Delta

class DailyGraph:
    def __init__(self, logger: Logger, width: int, height: int):
        self.logger = logger
        self.width = width
        self.height = height
        self.daily: list[float] = []
        self.accumulates: list[float] = []
        self.eixo: list[float] = []
        self.__collect()

    def __collect(self):
        days_minutes = self.logger.week.resume()
        sorted_keys = sorted(days_minutes.keys())
        self.daily = [0]
        self.accumulates = [0]
        for item in sorted_keys:
            self.daily.append(days_minutes[item].elapsed_seconds)
            self.accumulates.append(self.accumulates[-1] + days_minutes[item].elapsed_seconds)
        
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

    def get_graph(self) -> list[Text]:
        # collected: list[float] = []
        # eixo: list[int] = []
        if not self.daily:
            return []

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
        self.eixo = [x / 7 for x in self.eixo]

        result: list[str] = plot_to_string(xs=[eixo, self.eixo], ys=[bar, accumulates], lines=[True, True], y_min=0,width=self.width, height=self.height, y_unit="%", x_unit="w")

        if isinstance(result, str):
            result = result.splitlines()
        lines: list[Text] = []
        for line in result:
            lines.append(Text.decode_raw(line))

        lines.append(Text().addf("C", " Máximo diário: ").addf("{C}", f"{Delta.format_h_min(max_daily)} ")
                     .add(" ").addf("M", " Acumulado: ").addf("M", f"{Delta.format_h_min(max_accumulates)} ")
                     .center(self.width))
        return lines
