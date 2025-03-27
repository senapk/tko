from tko.settings.logger import Logger
from uniplot import plot_to_string # type: ignore

class WeekGraph:
    def __init__(self, width: int, height: int, week_mode: bool = False):
        self.width = width
        self.height = height
        self.week_mode = week_mode
        self.collected: list[float] = []
        self.eixo: list[float] = []
        self.__collect()

    def __collect(self):
        logger = Logger.get_instance()
        days_minutes = logger.week.resume()
        if self.week_mode:
            self.collected = [0]
            for day, value in days_minutes.items():
                week_day = value.weed_day
                elapsed = value.elapsed
                if week_day == "Sunday":
                    self.collected.append(0)
                self.collected[-1] += elapsed

        else:
            self.collected = []
            for value in days_minutes.values():
                self.collected.append(value.elapsed)
        # convertendo de minutos pra horas/minutos
        for i in range(len(self.collected)):
            value = self.collected[i]
            hours = value // 60
            minutes = value % 60
            self.collected[i] = hours + minutes / 100.0
        self.eixo = list(range(len(self.collected)))
        # self.eixo = list(range(len(collected)))

    def get_collected(self) -> list[str]:
        output: list[str] = []
        for value in self.collected:
            output.append(f"{value:.2f}")
        for i in range(len(output)):
            output[i] = output[i].replace(".", ":").rjust(5, " ")
        return output

    def get_graph(self) -> list[str]:
        collected: list[float] = []
        eixo: list[int] = []
        if self.week_mode:
            title = " (horas / semana)"
            week = 1
            for value in self.collected:
                eixo.append(week)
                collected.append(0)
                eixo.append(week)
                collected.append(value)
                eixo.append(week)
                collected.append(0)
                week += 1
            result = plot_to_string(xs=eixo, ys=collected, title=title, lines=True, y_min=0, width=self.width, height=self.height, y_unit="h", x_unit="s")
        else:
            title = " (horas /  dia  )"
            day = 1
            for value in self.collected:
                eixo.append(day)
                collected.append(0)
                eixo.append(day)
                collected.append(value)
                eixo.append(day)
                collected.append(0)
                day += 1

            result = plot_to_string(xs=eixo, ys=collected, title=title, lines=True, y_min=0, width=self.width, height=self.height, y_unit="h", x_unit="d")
        if isinstance(result, str):
            return result.splitlines()
        return result
