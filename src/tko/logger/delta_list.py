from tko.logger.delta import Delta, DeltaMode
from tko.logger.log_item_base import LogItemBase


class DeltaList:
    def __init__(self):
        self.delta_map: dict[str, Delta] = {}
        self.base_list: list[tuple[Delta, LogItemBase]] = []

    def add_item(self, mode: DeltaMode, item: LogItemBase) -> None:
        last_delta: Delta | None = None
        if self.base_list:
            last_delta, _ = self.base_list[-1]
        delta = Delta.create_from(mode, last_delta, item.get_datetime())
        self.delta_map[item.label] = delta
        self.base_list.append((delta, item))