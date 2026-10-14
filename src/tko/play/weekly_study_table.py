"""Render repository study time as one row per calendar week."""

from __future__ import annotations

from datetime import date, timedelta

from tko.logger.daily_listener import DayInfo
from tko.logger.logger import Logger
from tko.util.rt import RT


class WeeklyStudyTable:
    """Build a Sunday-to-Saturday table from the repository daily log."""

    def __init__(self, logger: Logger, portuguese: bool = True) -> None:
        self.logger: Logger = logger
        self.portuguese: bool = portuguese

    @staticmethod
    def _format_time(elapsed_seconds: int) -> str:
        if elapsed_seconds <= 0:
            return ""
        total_minutes: int = max(0, elapsed_seconds) // 60
        hours: int
        minutes: int
        hours, minutes = divmod(total_minutes, 60)
        if hours >= 10:
            return f"{hours}h"
        return f"{hours}h{minutes:02d}"

    def get_table(self) -> list[RT]:
        days_info: dict[str, DayInfo] = self.logger.daily.resume()
        if not days_info:
            message: str = "Nenhum tempo de estudo registrado." if self.portuguese else "No study time recorded."
            return [RT(message)]

        elapsed_by_day: dict[date, int] = {
            date.fromisoformat(day): info.elapsed_seconds
            for day, info in days_info.items()
        }
        dates: list[date] = sorted(elapsed_by_day)
        first_date: date = dates[0]
        last_date: date = dates[-1]
        first_sunday: date = first_date - timedelta(days=(first_date.weekday() + 1) % 7)
        last_sunday: date = last_date - timedelta(days=(last_date.weekday() + 1) % 7)

        weekdays: tuple[str, ...] = (
            ("Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb")
            if self.portuguese
            else ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        )
        widths: tuple[int, ...] = (5, 4, 4, 4, 4, 4, 4, 4)

        def border() -> str:
            return "+" + "+".join("-" * width for width in widths) + "+"

        def row(cells: tuple[str, ...]) -> str:
            return "|" + "|".join(
                f"{cell:^{width}}" for cell, width in zip(cells, widths, strict=True)
            ) + "|"

        lines: list[RT] = [RT(border()), RT(row(("Sem.", *weekdays))), RT(border())]

        week: date = last_sunday
        while week >= first_sunday:
            cells: list[str] = []
            for offset in range(7):
                day: date = week + timedelta(days=offset)
                seconds: int = elapsed_by_day.get(day, 0)
                cells.append(self._format_time(seconds))
            lines.append(RT(row((week.strftime("%d/%m"), *cells))))
            lines.append(RT(border()))
            week -= timedelta(days=7)

        return lines
