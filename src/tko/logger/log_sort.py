import sys # type: ignore

from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.logger.log_item_self import LogItemSelf
from tko.logger.delta import Delta, DeltaMode
from tko.i18n import Msg, t
from icecream import ic # type: ignore


_LOGGER_INVALID_ITEM_TYPE = Msg(
    pt="Tipo de item inválido",
    en="Invalid Item Type",
)

class LogSort:
    def __init__(self):
        self.base_list: list[tuple[Delta, LogItemBase]] = []
        self.exec_list: list[tuple[Delta, LogItemExec]] = []
        self.diff_list: list[tuple[Delta, LogItemExec]] = []
        self.move_list: list[tuple[Delta, LogItemMove]] = []
        self.self_list: list[tuple[Delta, LogItemSelf]] = []

    def add_item(self, mode: DeltaMode, item: LogItemBase) -> None:
        delta = LogItemBase.add_to_list(mode, self.base_list, item)
        self.__sort_by_instance(delta, item)
    
    def __sort_by_instance(self, delta: Delta, base: LogItemBase) -> None:
        if isinstance(base, LogItemExec):
            self.exec_list.append((delta, base))
            if base.get_size() > 0:
                self.diff_list.append((delta, base))
        elif isinstance(base, LogItemMove):
            self.move_list.append((delta, base))
        elif isinstance(base, LogItemSelf):
            self.self_list.append((delta, base))
        else:
            raise ValueError(t(_LOGGER_INVALID_ITEM_TYPE))
        
    