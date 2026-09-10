"""Small, dependency-free charts for the terminal UI."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from tko.util.rt import RT, Run
from tko.util.text_style import TextStyle


@dataclass(frozen=True)
class Series:
    points: list[tuple[float, float]]
    color: str
    line: bool = True


@dataclass(frozen=True)
class _Cell:
    glyph: str = " "
    style: TextStyle = TextStyle()


class TerminalChart:
    """Rasterize numeric series with labelled axes into styled terminal rows."""

    def __init__(
        self,
        width: int,
        height: int,
        series: list[Series],
        y_min: float = 0,
        y_max: float | None = None,
    ):
        self.width = max(width, 5)
        self.height = max(height, 3)
        self.series = series
        self.y_min = y_min
        values = [y for item in series for _, y in item.points if isfinite(y)]
        self.y_max = y_max if y_max is not None else (max(values) if values else y_min + 1)
        if self.y_max <= self.y_min:
            self.y_max = self.y_min + 1

    def render(self) -> list[RT]:
        x_values = [x for item in self.series for x, y in item.points if isfinite(x) and isfinite(y)]
        x_min = min(x_values, default=0)
        x_max = max(x_values, default=x_min + 1)
        if x_max <= x_min:
            x_max = x_min + 1

        y_ticks = self._ticks(self.y_min, self.y_max)
        label_width = min(
            max(3, *(len(self._format(value)) for value in y_ticks)),
            self.width - 3,
        )
        plot_width = max(self.width - label_width - 1, 2)
        plot_height = max(self.height - 1, 1)
        cells = [[_Cell() for _ in range(plot_width)] for _ in range(plot_height)]

        # The bottom raster row is the X axis. Data is painted afterwards so
        # points at y=0 remain visible.
        for col in range(plot_width):
            cells[-1][col] = _Cell("─")
        x_ticks = self._ticks(x_min, x_max)
        x_tick_columns = [self._x_to_column(value, x_min, x_max, plot_width) for value in x_ticks]
        for col in x_tick_columns:
            cells[-1][col] = _Cell("┬")

        for item in self.series:
            points = [
                self._point(x, y, x_min, x_max, plot_width, plot_height)
                for x, y in item.points
                if isfinite(x) and isfinite(y)
            ]
            style = TextStyle.parse(item.color)
            if item.line:
                for start, end in zip(points, points[1:]):
                    self._line(cells, start, end, _Cell("▓", style))
                if len(points) == 1:
                    self._put(cells, points[0], _Cell("▓", style))
            else:
                for point in points:
                    self._put(cells, point, _Cell("█", style))

        tick_rows: dict[int, str] = {}
        for value in y_ticks:
            row = self._y_to_row(value, plot_height)
            tick_rows.setdefault(row, self._fit_label(self._format(value), label_width))
        output: list[RT] = []
        for row_index, row in enumerate(cells):
            label = tick_rows.get(row_index, "")
            axis = "┼" if row_index == plot_height - 1 else ("┤" if label else "│")
            output.append(RT.from_runs(self._runs([_Cell(label.rjust(label_width) + axis)] + row)))
        output.append(self._x_labels(label_width + 1, x_ticks, x_tick_columns))
        return output

    @staticmethod
    def _ticks(lower: float, upper: float) -> list[float]:
        return [upper, (lower + upper) / 2, lower]

    @staticmethod
    def _format(value: float) -> str:
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")

    @staticmethod
    def _fit_label(label: str, width: int) -> str:
        return label if len(label) <= width else label[:width]

    @staticmethod
    def _x_to_column(value: float, x_min: float, x_max: float, plot_width: int) -> int:
        column = round((value - x_min) / (x_max - x_min) * (plot_width - 1))
        return min(max(column, 0), plot_width - 1)

    def _y_to_row(self, value: float, plot_height: int) -> int:
        normalized = min(max(value, self.y_min), self.y_max)
        row = round((self.y_max - normalized) / (self.y_max - self.y_min) * (plot_height - 1))
        return min(max(row, 0), plot_height - 1)

    def _point(
        self, x: float, y: float, x_min: float, x_max: float, plot_width: int, plot_height: int
    ) -> tuple[int, int]:
        return self._x_to_column(x, x_min, x_max, plot_width), self._y_to_row(y, plot_height)

    def _x_labels(self, prefix_width: int, ticks: list[float], columns: list[int]) -> RT:
        row = [" "] * self.width
        occupied = [False] * self.width
        for value, column in zip(ticks, columns):
            label = self._format(value)
            start = prefix_width + column - len(label) // 2
            start = min(max(start, prefix_width), self.width - len(label))
            end = start + len(label)
            if any(occupied[start:end]):
                continue
            row[start:end] = label
            occupied[start:end] = [True] * len(label)
        return RT("".join(row))

    @staticmethod
    def _put(cells: list[list[_Cell]], point: tuple[int, int], cell: _Cell) -> None:
        col, row = point
        cells[row][col] = cell

    def _line(self, cells: list[list[_Cell]], start: tuple[int, int], end: tuple[int, int], cell: _Cell) -> None:
        x0, y0 = start
        x1, y1 = end
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1, 1 if y0 < y1 else -1)
        error = dx + dy
        while True:
            self._put(cells, (x0, y0), cell)
            if (x0, y0) == (x1, y1):
                return
            twice_error = 2 * error
            if twice_error >= dy:
                error += dy
                x0 += sx
            if twice_error <= dx:
                error += dx
                y0 += sy

    @staticmethod
    def _runs(cells: list[_Cell]) -> list[Run]:
        runs: list[Run] = []
        for cell in cells:
            if runs and runs[-1][0] == cell.style:
                style, text = runs[-1]
                runs[-1] = style, text + cell.glyph
            else:
                runs.append((cell.style, cell.glyph))
        return runs
