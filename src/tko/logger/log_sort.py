from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.logger.log_item_self import LogItemSelf
from tko.logger.delta import Delta


class LogSort:
    def __init__(self):
        self.base_list: list[tuple[Delta, LogItemBase]] = []
        self.exec_list: list[tuple[Delta, LogItemExec]] = []
        self.diff_list: list[tuple[Delta, LogItemExec]] = []
        self.move_list: list[tuple[Delta, LogItemMove]] = []
        self.self_list: list[tuple[Delta, LogItemSelf]] = []

    def add_item(self, mode: Delta.Mode, base: LogItemBase) -> tuple[Delta, LogItemBase]:
        last_delta: Delta | None = None
        if self.base_list:
            last_delta, _ = self.base_list[-1]
        delta = Delta().create(mode, last_delta, base.get_datetime())
        self.base_list.append((delta, base))
        self.__sort_by_instance(delta, base)
        return delta, base

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
            raise ValueError("Invalid Item Type")
        

    @staticmethod
    def add_to_list(
        mode: Delta.Mode, base_list: list[tuple[Delta, LogItemBase]], item: LogItemBase
    ) -> tuple[Delta, LogItemBase]:
        last_delta: Delta | None = None
        if base_list:
            last_delta, _ = base_list[-1]
        delta = Delta().create(mode, last_delta, item.get_datetime())
        base_list.append((delta, item))
        return delta, item