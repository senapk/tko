from __future__ import annotations
import datetime as dt
import enum


class Delta:
    format = '%Y-%m-%d %H:%M:%S'
    def __init__(self):
        self.datetime: dt.datetime = dt.datetime.fromordinal(1)
        self.elapsed: dt.timedelta = dt.timedelta()
        self.accumulated: dt.timedelta = dt.timedelta()

    def __str__(self) -> str:
        return f"datetime:{Delta.encode_format(self.datetime)}, elapsed:{Delta.encode_timedelta(self.elapsed)}, acc:{Delta.encode_timedelta(self.accumulated)}"


    @staticmethod
    def encode_timedelta(elapsed: dt.timedelta) -> str:
        total_seconds = elapsed.total_seconds()
        minutes = round(total_seconds // 60)
        seconds = round(total_seconds) % 60
        return f'{minutes:03d}:{seconds:02d}' 
    
    def create(self, mode: Mode, last_item: Delta | None, datetime: dt.datetime) -> Delta:
        if mode.action == Delta.Mode.Action.without_inc_time:
            return self.__create_without_inc_time(last_item, datetime)
        elif mode.action == Delta.Mode.Action.incrementing_time:
            return self.__create_incrementing_time(last_item, datetime)
        elif mode.action == Delta.Mode.Action.with_time_threshold:
            return self.__create_with_time_threshold(last_item, datetime, mode.minutes_limit)
        else:
            raise ValueError(f'Unknown action {mode.action}')

    def __create_without_inc_time(self, last_item: Delta | None, datetime: dt.datetime) -> Delta:
        if last_item is None:
            self.datetime = datetime
            self.elapsed = dt.timedelta()
            return self

        self.datetime = datetime
        self.elapsed = datetime - last_item.datetime
        self.accumulated = last_item.accumulated
        return self

    def __create_incrementing_time(self, last_item: Delta | None, datetime: dt.datetime) -> Delta:
        self.__create_without_inc_time(last_item, datetime)
        seconds = self.elapsed.total_seconds()
        if last_item is not None and seconds > 0:
            self.accumulated += self.elapsed
        return self

    def __create_with_time_threshold(self, last_item: Delta | None, datetime: dt.datetime, minutes_limit: int) -> Delta:
        self.__create_without_inc_time(last_item, datetime)
        seconds = self.elapsed.total_seconds()
        if last_item is not None and seconds > 0 and seconds / 60 < minutes_limit:
            self.accumulated += self.elapsed
        return self

    @staticmethod
    def now() -> tuple[str, dt.datetime]:
        now = dt.datetime.now()
        return now.strftime(Delta.format), now

    @staticmethod
    def decode_format(value: str) -> dt.datetime:
        return dt.datetime.strptime(value, Delta.format)
    
    @staticmethod
    def encode_format(value: dt.datetime) -> str:
        return dt.datetime.strftime(value, Delta.format)
    
    @staticmethod
    def format_h_min(hours: float) -> str:
        if hours < 0:
            return "00:00"
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h:02d}h {m:02d}m"

    @staticmethod
    def week_day(day: str) -> str:
        date = dt.datetime.strptime(day, '%Y-%m-%d')
        return date.strftime('%A')

    @staticmethod
    def next_day(day: str) -> str:
        date = dt.datetime.strptime(day, '%Y-%m-%d')
        return (date + dt.timedelta(days=1)).strftime('%Y-%m-%d')

    class Mode:        
        def __init__(self, action: Action, minutes_limit: int = 60):
            self.action = action
            self.minutes_limit = minutes_limit

        def __str__(self) -> str:
            return f'{self.action.name} {self.minutes_limit}'

        class Action(enum.Enum):
            without_inc_time = 1
            incrementing_time = 2
            with_time_threshold = 3