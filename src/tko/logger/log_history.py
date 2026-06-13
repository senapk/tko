from __future__ import annotations
from tko.config.run_settings import RunSettings
from tko.logger.log_item_base import LogItemBase, LogItemBaseType
from tko.logger.log_item_self import LogItemSelf
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.logger.delta import Delta
from tko.i18n import Msg
from tko.repository.repository_paths import RepositoryPaths
import datetime as dt

from tko.util.decoder import Decoder
from typing import Callable
from pathlib import Path
import sys # type: ignore


_LOGGER_LOG_FOLDER_NOT_DIR = Msg(
    pt="A pasta de log '{log_folder}' não é um diretório.",
    en="Log folder '{log_folder}' is not a directory.",
)

class LogHistory:

    def __init__(self, rep_folder: Path, rs: RunSettings, listeners: list[Callable[[LogItemBase, bool], None]] | None = None):
        if listeners is None:
            listeners = []
        self.paths = RepositoryPaths(rep_folder, rs)
        self.log_folder: Path = self.paths.log_folder
        self.listeners: list[Callable[[LogItemBase, bool], None]] = listeners
        self.entries: dict[str, LogItemBase] = {}
        #self.entries.extend(self.__load_old_log().values())
        self.entries.update({str(item): item for item in self.__load_daily_log_folder()})
        # avoid duplicated entries
        sorted_entries: list[LogItemBase] = sorted([item for item in self.entries.values()], key=lambda x: x.get_datetime())
        
        for item in sorted_entries:
            for listener in self.listeners:
                listener(item, False)

    # def __load_old_log(self) -> dict[dt.datetime, LogItemBase]:
    #     self.old_log_file = self.paths.get_old_history_file()
    #     loader = OldLogLoader(self.paths.get_repo_root_dir())
    #     return loader.base_dict

    def get_entries(self) -> list[LogItemBase]:
        return list(self.entries.values())

    def get_log_folder(self) -> Path:
        return self.log_folder


    @staticmethod
    def log_file_for_day(folder: Path, datetime: dt.datetime) -> Path:
        date_str = datetime.strftime("%Y-%m-%d")
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{date_str}.log"

    def append_new_action(self, item_base: LogItemBase) -> LogItemBase:
        now_str, now_dt = Delta.now()
        if item_base.get_datetime() == dt.datetime.fromordinal(1):
            item_base.set_timestamp(now_str, now_dt)
        self.entries[str(item_base)] = item_base
        for listener in self.listeners:
            listener(item_base, True)

        log_folder = self.get_log_folder()
        log_file = LogHistory.log_file_for_day(log_folder, item_base.get_datetime())
        with open(log_file, 'a', encoding="utf-8", newline='') as file:
            file.write(f'{item_base.encode_line()}\n')
        return item_base

    def __load_daily_log_folder(self) -> list[LogItemBase]:
        log_folder = self.paths.log_folder
        if not log_folder.exists():
            return []
        if not log_folder.is_dir():
            raise ValueError(str(_LOGGER_LOG_FOLDER_NOT_DIR).format(log_folder=log_folder))
        files = log_folder.iterdir()

        files_path = [f for f in files if f.suffix == '.log']
        if not files_path:
            return []
        # begin with the older file
        files_path.sort()
        entries: list[LogItemBase] = []
        for file in files_path:
            # verify if name is in the format YYYY-MM-DD.log
            name = file.stem
            try:
                dt.datetime.strptime(name, "%Y-%m-%d")
            except ValueError:
                continue
            content = Decoder.load(file)
            for line in content.splitlines():
                item: LogItemBase | None = LogHistory.decode_line(line)
                if item is not None:
                    entries.append(item)
        return entries
    
    @staticmethod
    def decode_line(line: str) -> LogItemBase | None:
        parts = line.strip().split(", ")
        if len(parts) < 2:
            return None
        item_type = LogItemBaseType(parts[1])
        if item_type == LogItemBaseType.MOVE:
            item = LogItemMove()
            if item.decode_line(parts):
                return item
        elif item_type == LogItemBaseType.EXEC:
            item = LogItemExec()
            if item.decode_line(parts):
                return item
        elif item_type == LogItemBaseType.SELF:
            item = LogItemSelf()
            if item.decode_line(parts):
                return item
        return None
