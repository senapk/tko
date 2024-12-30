from __future__ import annotations
import csv
import hashlib
import datetime
from rota.settings.settings import Settings
from rota.util.daily import DailyLog
from rota.game.task import Task
from rota.util.decoder import Decoder
import enum
import os

from abc import ABC, abstractmethod


class LogAction(enum.Enum):
    NONE = 'NONE'
    OPEN = 'OPEN'
    DOWN = 'DOWN'
    FREE = 'FREE' 
    TEST = 'TEST' # CORRECT|WRONG|COMPILE|RUNTIME
    SELF = 'SELF' # int
    PROG = 'PROG' # int
    QUIT = 'QUIT'
    PICK = 'PICK'
    BACK = 'BACK'


class ActionData:
    def __init__(self, timestamp: str, action_value: str, task: str = "", payload: str = ""):
        self.timestamp = timestamp
        self.action_value: str = action_value
        self.task_key = task
        self.payload = payload
        self.hash = ""

    def __str__(self):
        return f'{self.timestamp}, {self.action_value}, {self.task_key}, {self.payload}'

    @staticmethod
    def generate_hash(action_data: ActionData, last_hash: str):
        comprimento = 6
        input_str = str(action_data) + last_hash
        hash_completo = hashlib.sha256(input_str.encode()).hexdigest()
        return hash_completo[:comprimento]  # Retorna os primeiros 'comprimento' caracteres do hash

    @staticmethod
    def parse_history_file(content: str) -> list[ActionData]:
        rows = content.split("\n")
        output: list[ActionData] = []
        for row in rows:
            row = row.strip()
            if row == "":
                continue
            items = row.split(",")
            if len(row) < 4:
                continue
            ad = ActionData(items[1], items[2], items[3], items[4])
            output.append(ad)
        return output

class LoggerStore(ABC):
    @abstractmethod
    def push_to_file(self, action_data: ActionData, last_hash: str):
        pass

    @abstractmethod
    def set_log_file(self, path: str):
        pass

    @abstractmethod
    def get_log_file(self) -> str | None:
        pass

    @abstractmethod
    def get_action_entries(self) -> list[ActionData]:
        pass

    @abstractmethod
    def get_last_hash(self) -> str:
        pass

class LoggerFS(LoggerStore):

    def __init__(self, settings: Settings):
        self.log_file: str | None = None
        self.settings = settings
    
    def set_log_file(self, log_file: str):
        self.log_file = log_file
        return self
    
    def get_log_file(self) -> str | None:
        return self.log_file
    
    def row_to_action_data(self, row: list[str]) -> ActionData | None:
        if len(row) < 5:
            return None
        hash = row[0]
        timestamp = row[1]
        action_value = row[2]
        task = row[3]
        payload = row[4]
        action_data = ActionData(timestamp, action_value, task, payload)
        action_data.hash = hash
        return action_data

    def push_to_file(self, action_data: ActionData, last_hash: str):
        log_file = self.get_log_file()
        if log_file is None:
            return
        action_data.hash = ActionData.generate_hash(action_data, last_hash)
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
        with open(log_file, 'a', encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            ad = action_data
            writer.writerow([ad.hash, ad.timestamp, ad.action_value, ad.task_key, ad.payload])
            return ad.hash

    def get_action_entries(self) -> list[ActionData]:
        log_file = self.get_log_file()
        if log_file is None:
            return []
        if not os.path.exists(log_file):
            return []
        encoding = Decoder.get_encoding(log_file)
        with open(log_file, 'r', encoding=encoding) as file:
            reader = csv.reader(file)
            rows = list(reader)
            output: list[ActionData] = []
            for row in rows:
                action_data = self.row_to_action_data(row)
                if action_data is not None:
                    output.append(action_data)
            return output

    def get_last_hash(self) -> str:
        return self.get_action_entries()[-1].hash if len(self.get_action_entries()) > 0 else ""

class LoggerMemory(LoggerStore):
    def __init__(self):
        self.entries: list[ActionData] = []

    def set_log_file(self, path: str):
        return self
    
    def get_log_file(self) -> str | None:
        return None

    def push_to_file(self, action_data: ActionData, last_hash: str):
        action_data.hash = ActionData.generate_hash(action_data, last_hash)
        self.entries.append(action_data)
        return action_data.hash

    def get_action_entries(self) -> list[ActionData]:
        return self.entries

    def get_last_hash(self) -> str:
        return self.entries[-1].hash if len(self.entries) > 0 else ""

class Logger:
    instance: None | Logger = None
    COMP_ERROR = "COMP"
    FREE_EXEC = "FREE"

    @staticmethod
    def get_instance() -> Logger:
        if Logger.instance is None:
            raise Exception("Logger not initialized")
        return Logger.instance

    def __init__(self, logger_store: LoggerStore):
        self.last_hash: str | None = None
        self.fs = logger_store
        self.daily: DailyLog | None = None

    def set_history_file(self, log_file: str):
        self.fs.set_log_file(log_file)
        return self
    
    @staticmethod
    def today() -> str:
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def set_daily(self, daily_file: str, tasks: dict[str, Task]):
        self.daily = DailyLog(daily_file)
        today = Logger.today()
        changed = False
        for task in tasks.values():
            if self.daily.log_task(today, task.key, task.coverage, task.autonomy, save_on_change=False):
                changed = True
        if changed:
            self.daily.save()
        return self

    def check_log_file_integrity(self) -> list[str]:
        entries = self.fs.get_action_entries()
        if len(entries) == 0:
            return []
        hash = entries[0].hash
        output: list[str] = []

        for i in range(1, len(entries)):
            calculated_hash = ActionData.generate_hash(entries[i], hash)
            if calculated_hash != entries[i].hash:
                output.append(f"Hash mismatch line {i + 1}: {str(entries[i])}")
            hash = calculated_hash
        return output

    def record_pick(self, task_key: str):
        self.__record_other_event(LogAction.PICK, task_key)

    def record_back(self, task_key: str):
        self.__record_other_event(LogAction.BACK, task_key)

    def record_down(self, task_key: str):
        self.__record_other_event(LogAction.DOWN, task_key)

    def record_compilation_error(self, task_key: str):
        self.__record_other_event(LogAction.TEST, task_key, self.COMP_ERROR)
    
    def record_test_result(self, task_key: str, result: int):
        self.__record_other_event(LogAction.TEST, task_key, str(result))

    def record_freerun(self, task_key: str):
        self.__record_other_event(LogAction.FREE, task_key)

    def record_self_grade(self, task_key: str, autonomy: int, ability: int):
        self.__record_other_event(LogAction.SELF, task_key, f"0{autonomy}{ability}")
    
    def record_progress(self, task_key: str, coverage: int):
        self.__record_other_event(LogAction.PROG, task_key, str(coverage))

    def record_open(self):
        self.__record_other_event(LogAction.OPEN)
    
    def record_quit(self):
        self.__record_other_event(LogAction.QUIT)

    def __record_other_event(self, action: LogAction, task_key: str = "", payload: str = ""):
        action_data = ActionData(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), action.value, task_key, payload)
        self.record_action_data(action_data)

    def get_last_hash(self) -> str:
        if self.last_hash is None:
            self.last_hash = self.fs.get_last_hash()
        return self.last_hash

    def record_action_data(self, action_data: ActionData):
        self.log_daily(action_data)
        self.last_hash = self.fs.push_to_file(action_data, self.get_last_hash())


    def log_daily(self, action_data: ActionData):
        if self.daily is None:
            return
        if action_data.action_value == LogAction.SELF.value:
            self.daily.log_task(Logger.today(), key=action_data.task_key, autonomy=int(action_data.payload))
        elif action_data.action_value == LogAction.PROG.value:
            self.daily.log_task(Logger.today(), key=action_data.task_key, coverage=int(action_data.payload))
        elif action_data.action_value == LogAction.TEST.value:
            try:
                result = int(action_data.payload)                
                self.daily.log_task(Logger.today(), key=action_data.task_key, coverage=result)
            except ValueError:
                pass