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

    def base_list(self) -> list[tuple[Delta, LogItemBase]]:
        return self.delta_list.base_list

    def exec_list(self) -> list[tuple[Delta, LogItemExec]]:
        output: list[tuple[Delta, LogItemExec]] = []
        for delta, item in self.delta_list.base_list:
            if isinstance(item, LogItemExec):
                output.append((delta, item))
        return output

    def diff_list(self) -> list[tuple[Delta, LogItemExec]]:
        output: list[tuple[Delta, LogItemExec]] = []
        for delta, item in self.delta_list.base_list:
            if isinstance(item, LogItemExec) and item.get_size() > 0:
                output.append((delta, item))
        return output
    
    def move_list(self) -> list[tuple[Delta, LogItemMove]]:
        output: list[tuple[Delta, LogItemMove]] = []
        for delta, item in self.delta_list.base_list:
            if isinstance(item, LogItemMove):
                output.append((delta, item))
        return output

    
    def self_list(self) -> list[tuple[Delta, LogItemSelf]]:
        output: list[tuple[Delta, LogItemSelf]] = []
        for delta, item in self.delta_list.base_list:
            if isinstance(item, LogItemSelf):
                output.append((delta, item))
        return output


    def add_item(self, mode: DeltaMode, item: LogItemBase) -> None:
        self.delta_list.add_item(mode, item)
            
    