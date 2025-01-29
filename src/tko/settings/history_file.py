from tko.settings.log_action import LogAction
from tko.util.decoder import Decoder

import csv
import datetime
import os
from typing import Callable

class HistoryFile:

    def __init__(self, history_file: str | None = None, listeners: list[Callable[[LogAction, bool], None]] = []):
        self.history_file: str | None = history_file
        self.listeners: list[Callable[[LogAction, bool], None]] = listeners
        self.entries: list[LogAction] = HistoryFile.__load_file(history_file)
        for entry in self.entries:
            for listener in self.listeners:
                listener(entry, False)

    def get_entries(self) -> list[LogAction]:
        return self.entries

    def get_log_file(self) -> str | None:
        return self.history_file

    def __append_action_data(self, action_data: LogAction):
        self.entries.append(action_data)
        for listener in self.listeners:
            listener(action_data, True)
        log_file = self.get_log_file()
        if log_file is None:
            return
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
        with open(log_file, 'a', encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            ad = action_data
            writer.writerow([ad.hash, ad.timestamp, ad.type_value, ad.task_key, ad.payload])

    def append_new_action(self, action: LogAction.Type, task_key: str = "", payload: str = ""):
        action_data = LogAction(action.value, task_key, payload)
        action_data.hash = LogAction.generate_hash(action_data, self.get_last_hash())
        action_data.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__append_action_data(action_data)

    @staticmethod
    def __row_to_action_data( row: list[str]) -> LogAction | None:
        if len(row) < 5:
            return None
        hash = row[0]
        timestamp = row[1]
        action_value = row[2]
        task = row[3]
        payload = row[4]
        action_data = LogAction(action_value, task, payload).set_hash(hash).set_timestamp(timestamp)
        return action_data

    @staticmethod
    def __load_file(history_file: str | None) -> list[LogAction]:
        if history_file is None:
            return []
        if not os.path.exists(history_file):
            return []
        encoding = Decoder.get_encoding(history_file)
        entries: list[LogAction] = []
        with open(history_file, 'r', encoding=encoding) as file:
            reader = csv.reader(file)
            rows = list(reader)
            for row in rows:
                action_data = HistoryFile.__row_to_action_data(row)
                if action_data is not None:
                    entries.append(action_data)
        return entries

    def get_last_hash(self) -> str:
        if len(self.entries) == 0:
            return ""
        return self.entries[-1].hash