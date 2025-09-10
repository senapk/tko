from __future__ import annotations
from tko.logger.old_log_loader import OldLogLoader
from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_self import LogItemSelf
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.logger.delta import Delta
from tko.settings.rep_paths import RepPaths
import datetime as dt

from tko.util.decoder import Decoder
from typing import Callable
import os


class LogHistory:

    def __init__(self, rep_folder: str, listeners: list[Callable[[LogItemBase, bool], None]] | None = None):
        if listeners is None:
            listeners = []
        self.paths = RepPaths(rep_folder)
        self.log_folder: str = self.paths.get_log_folder()
        self.listeners: list[Callable[[LogItemBase, bool], None]] = listeners
        self.entries: dict[dt.datetime, LogItemBase] = {}
        self.entries.update(self.__load_old_log())
        self.entries.update(self.__load_daily_log_folder())
        # avoid duplicated entries
        sorted_entries = sorted(self.entries.items(), key=lambda x: x[0])
        
        for _, item in sorted_entries:
            for listener in self.listeners:
                listener(item, False)

    def __load_old_log(self) -> dict[dt.datetime, LogItemBase]:
        self.old_log_file = self.paths.get_old_history_file()
        loader = OldLogLoader(self.paths.get_rep_dir())
        return loader.base_dict

    def get_entries(self) -> dict[dt.datetime, LogItemBase]:
        return self.entries

    def get_log_folder(self) -> str | None:
        return self.log_folder


    @staticmethod
    def log_file_for_day(folder: str, datetime: dt.datetime) -> str:
        date_str = datetime.strftime("%Y-%m-%d")
        if not os.path.exists(folder):
            os.makedirs(folder)
        return os.path.abspath(os.path.join(folder, f"{date_str}.log"))

    def append_new_action(self, item_base: LogItemBase) -> LogItemBase:
        now_str, now_dt = Delta.now()
        item_base.set_timestamp(now_str, now_dt)
        self.entries[now_dt] = item_base
        for listener in self.listeners:
            listener(item_base, True)

        log_folder = self.get_log_folder()
        if log_folder is not None:
            log_file = LogHistory.log_file_for_day(log_folder, item_base.get_datetime())
            with open(log_file, 'a', encoding="utf-8", newline='') as file:
                file.write(f'{item_base.encode_line()}\n')
        return item_base

    def __load_daily_log_folder(self) -> dict[dt.datetime, LogItemBase]:
        log_folder = self.paths.get_log_folder()
        if not os.path.exists(log_folder):
            return {}
        if not os.path.isdir(log_folder):
            raise ValueError(f"Log folder '{log_folder}' is not a directory.")
        files = os.listdir(log_folder)
        files_path = [os.path.join(log_folder, f) for f in files if f.endswith('.log')]
        if not files_path:
            return {}
        # begin with the older file
        files_path.sort()
        entries: dict[dt.datetime, LogItemBase] = {}
        for file in files_path:
            encoding = Decoder.get_encoding(file)
            with open(file, 'r', encoding=encoding) as f:
                for line in f:
                    item: LogItemBase | None = LogHistory.decode_line(line)
                    if item is not None:
                        entries[item.get_datetime()] = item
        return entries
    
    @staticmethod
    def decode_line(line: str) -> LogItemBase | None:
        parts = line.strip().split(", ")
        if len(parts) < 2:
            return None
        item_type = LogItemBase.Type(parts[1])
        if item_type == LogItemBase.Type.MOVE:
            item = LogItemMove()
            if item.decode_line(parts):
                return item
        elif item_type == LogItemBase.Type.EXEC:
            item = LogItemExec()
            if item.decode_line(parts):
                return item
        elif item_type == LogItemBase.Type.SELF:
            item = LogItemSelf()
            if item.decode_line(parts):
                return item
        return None
