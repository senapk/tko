import sys # type: ignore

from tko.logger.delta_list import DeltaList
from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.logger.log_item_self import LogItemSelf
from tko.logger.delta import Delta, DeltaMode
import datetime as dt
from icecream import ic # type: ignore


class LogSort:
    def __init__(self):
        self.delta_list = DeltaList()
        self.sequential_ocurrences: int = 0
        self.__cached_diff_list: list[tuple[Delta, LogItemExec]] = []
        self.__cached_exec_list: list[tuple[Delta, LogItemExec]] = []
        self.__cached_move_list: list[tuple[Delta, LogItemMove]] = []
        self.__cached_self_list: list[tuple[Delta, LogItemSelf]] = []

    @property
    def key(self) -> str | None:
        if self.delta_list.base_list:
            return self.delta_list.base_list[0][1].get_key()
        return None

    @property
    def base_list(self) -> list[tuple[Delta, LogItemBase]]:
        return self.delta_list.base_list

    @property
    def exec_list(self) -> list[tuple[Delta, LogItemExec]]:
        return self.__cached_exec_list

    @property
    def diff_list(self) -> list[tuple[Delta, LogItemExec]]:
        return self.__cached_diff_list
    
    @property
    def move_list(self) -> list[tuple[Delta, LogItemMove]]:
        return self.__cached_move_list

    @property
    def self_list(self) -> list[tuple[Delta, LogItemSelf]]:
        return self.__cached_self_list

    def is_continuous_action(self, mode: DeltaMode, item: LogItemBase) -> bool:
        last_delta: Delta | None = None if not self.base_list else self.base_list[-1][0]
        delta = Delta.create_from(mode, last_delta, item.get_datetime())
        if last_delta is None:
            return False
        if delta.elapsed == dt.timedelta(seconds=0):
            return True
        return delta.accumulated > last_delta.accumulated

    def add_item(self, mode: DeltaMode, item: LogItemBase) -> None:
        if not self.is_continuous_action(mode, item):
            self.sequential_ocurrences += 1
        self.delta_list.add_item(mode, item)
        delta = self.delta_list.base_list[-1][0]
        if isinstance(item, LogItemExec):
            self.__cached_exec_list.append((delta, item))
            if item.get_size() > 0:
                self.__cached_diff_list.append((delta, item))
        elif isinstance(item, LogItemMove):
            self.__cached_move_list.append((delta, item))
        elif isinstance(item, LogItemSelf):
            self.__cached_self_list.append((delta, item))
            
    