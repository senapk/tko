import sys # type: ignore

from tko.logger.delta_list import DeltaList
from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.logger.log_item_self import LogItemSelf
from tko.logger.delta import Delta, DeltaMode
from icecream import ic # type: ignore


class LogSort:
    def __init__(self):
        self.delta_list = DeltaList()
        self.__cached_diff_list: list[tuple[Delta, LogItemExec]] = []
        self.__cached_exec_list: list[tuple[Delta, LogItemExec]] = []
        self.__cached_move_list: list[tuple[Delta, LogItemMove]] = []
        self.__cached_self_list: list[tuple[Delta, LogItemSelf]] = []

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

    def add_item(self, mode: DeltaMode, item: LogItemBase) -> None:
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
            
    