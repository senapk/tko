from __future__ import annotations
import datetime as dt
import enum
from tko.i18n import Msg


_LOGGER_UNKNOWN_ACTION = Msg.text(
    pt="Ação desconhecida {action}",
    en="Unknown action {action}",
)

class DeltaAction(enum.Enum):
    without_inc_time = 1
    incrementing_time = 2
    with_time_threshold = 3

class DeltaMode:        
    def __init__(self, action: DeltaAction, minutes_limit: int = 60):
        self.action = action
        self.minutes_limit = minutes_limit

    def __str__(self) -> str:
        return f'{self.action.name} {self.minutes_limit}'



class Delta:
    format = '%Y-%m-%d %H:%M:%S'
    def __init__(self):
        self.mode: DeltaMode | None = None
        self.datetime: dt.datetime = dt.datetime.fromordinal(1)
        self.elapsed: dt.timedelta = dt.timedelta() # time elapsed since last item
        self.accumulated: dt.timedelta = dt.timedelta() # total accumulated

    def __str__(self) -> str:
        return f"datetime:{Delta.encode_format(self.datetime)}, elapsed:{Delta.encode_timedelta(self.elapsed)}, acc:{Delta.encode_timedelta(self.accumulated)}"


    @staticmethod
    def encode_timedelta(elapsed: dt.timedelta) -> str:
        total_seconds = elapsed.total_seconds()
        minutes = round(total_seconds // 60)
        seconds = round(total_seconds) % 60
        return f'{minutes:03d}:{seconds:02d}'
    
    @staticmethod
    def create_from(mode: DeltaMode, last_item: Delta | None, datetime: dt.datetime) -> Delta:
        delta = Delta()
        delta.mode = mode
        if mode.action == DeltaAction.without_inc_time:
            return delta.__create_without_inc_time(last_item, datetime)
        elif mode.action == DeltaAction.incrementing_time:
            return delta.__create_incrementing_time(last_item, datetime)
        elif mode.action == DeltaAction.with_time_threshold:
            return delta.__create_with_time_threshold(last_item, datetime, mode.minutes_limit)
        else:
            raise ValueError(_LOGGER_UNKNOWN_ACTION.t().format(action=mode.action))

    def __create_without_inc_time(self, last_item: Delta | None, datetime: dt.datetime) -> Delta:
        if last_item is None:
            self.datetime = datetime
            self.elapsed = dt.timedelta(seconds=0)
            return self

        self.datetime = datetime
        if last_item.datetime < datetime:
            self.elapsed = datetime - last_item.datetime
        self.accumulated = last_item.accumulated
        return self

    def __create_incrementing_time(self, last_item: Delta | None, datetime: dt.datetime) -> Delta:
        self.__create_without_inc_time(last_item, datetime)
        if last_item is not None and self.elapsed >= dt.timedelta(seconds=0):
            self.accumulated += self.elapsed
        return self

    def __create_with_time_threshold(self, last_item: Delta | None, datetime: dt.datetime, minutes_limit: int) -> Delta:
        self.__create_without_inc_time(last_item, datetime)
        if last_item is not None and self.elapsed >= dt.timedelta(seconds=0) and self.elapsed < dt.timedelta(minutes=minutes_limit):
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
            return "00h 00m"
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h:02d}h {m:02d}m"
    
    @staticmethod
    def format_hhmmss(seconds: float) -> str:
        h = int(seconds / 3600)
        r = int(seconds) % 3600
        m = int(r / 60)
        s = int(r % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    @staticmethod
    def parse_hhmmss(value: str) -> dt.timedelta:
        parts = value.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid time format: {value}")
        h, m, s = parts
        return dt.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    @staticmethod
    def week_day(day: str) -> str:
        date = dt.datetime.strptime(day, '%Y-%m-%d')
        return date.strftime('%A')

    @staticmethod
    def next_day(day: str) -> str:
        date = dt.datetime.strptime(day, '%Y-%m-%d')
        return (date + dt.timedelta(days=1)).strftime('%Y-%m-%d')

    