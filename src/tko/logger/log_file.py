from tko.logger.log_item_base import LogItemBase
from tko.logger.log_enum_item import LogEnumItem
from tko.logger.log_item_self import LogItemSelf
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_enum_item import LogEnumItem
from tko.logger.log_item_move import LogItemMove

from tko.util.decoder import Decoder

import datetime
import os
from typing import Callable

class LogFile:

    def __init__(self, history_file: str | None = None, listeners: list[Callable[[LogItemBase, bool], None]] = []):
        self.history_file: str | None = history_file
        self.listeners: list[Callable[[LogItemBase, bool], None]] = listeners
        self.entries: list[LogItemBase] = LogFile.__load_file(history_file)
        for entry in self.entries:
            for listener in self.listeners:
                listener(entry, False)

    def get_entries(self) -> list[LogItemBase]:
        return self.entries

    def get_log_file(self) -> str | None:
        return self.history_file

    def __append_action_data(self, item_base: LogItemBase):
        self.entries.append(item_base)
        for listener in self.listeners:
            listener(item_base, True)
        log_file = self.get_log_file()
        if log_file is None:
            return
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
        with open(log_file, 'a', encoding="utf-8", newline='') as file:
            file.write(f'{item_base.encode_line()}\n')

    def append_new_action(self, item: LogItemBase) -> LogItemBase:
        item.set_timestamp(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.__append_action_data(item)
        return item

    @staticmethod
    def __load_file(history_file: str | None) -> list[LogItemBase]:
        if history_file is None:
            return []
        if not os.path.exists(history_file):
            return []
        encoding = Decoder.get_encoding(history_file)
        entries: list[LogItemBase] = []
        with open(history_file, 'r', encoding=encoding) as file:
            for line in file:
                parts = line.strip().split(", ")
                if len(parts) < 2:
                    continue
                
        return entries
    
    def decode_line(self, line: str) -> LogItemBase | None:
        parts = line.strip().split(", ")
        if len(parts) < 2:
            return None
        item_type = LogEnumItem(parts[1])
        if item_type == LogEnumItem.MOVE:
            item = LogItemMove()
            if item.decode_line(parts):
                return item
        elif item_type == LogEnumItem.EXEC:
            item = LogItemExec()
            if item.decode_line(parts):
                return item
        elif item_type == LogEnumItem.SELF:
            item = LogItemSelf()
            if item.decode_line(parts):
                return item
        return None
