from tko.game.task import Task

from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.logger.log_item_self import LogItemSelf
from tko.settings.rep_paths import RepPaths
from tko.util.decoder import Decoder
import enum
import csv
import os

class LogAction:
    def __init__(self, hash: str, timestamp: str, action: str, task: str, payload: str):
        self.hash = hash
        self.timestamp = timestamp
        self.action = action
        self.task = task
        self.payload = payload

class AType(enum.Enum):
    NONE = 'NONE'
    OPEN = 'OPEN' # Open program
    QUIT = 'QUIT' # Quit program
    DOWN = 'DOWN' # Down problem
    FREE = 'FREE' # Free Compile and RUN
    FAIL = 'FAIL' # Compile error or Execution error
    TEST = 'TEST' # run test and Coverage %
    SELF = 'SELF' # {c:{coverage}, a:{approach}, s:{autonomy}} after added {clear:%d, fun:%d, easy:%d}
    PICK = 'PICK' # Enter problem
    BACK = 'BACK' # Leave problem
    PROG = 'PROG' # deprecated
    SIZE = 'SIZE' # Problem files changes "{line_count:%d}"

class OldLogLoader:
    def __init__(self, rep_folder: str):
        self.rep_folder = rep_folder
        self.paths = RepPaths(rep_folder)
        self.base_list: list[LogItemBase] = []
        self.base_dict: dict[str, LogItemBase] = {}

        self.old_log_file = self.paths.get_old_history_file()
        self.entries: list[LogAction] = self.__load_file(self.old_log_file)
        for e in self.entries:
            item = OldLogLoader.__convert_to_base_list(e)
            if item is not None:
                self.base_list.append(item)
                self.base_dict[item.get_timestamp()] = item

    @staticmethod
    def decode_self(e: LogAction) -> LogItemSelf:
        item = LogItemSelf().set_timestamp(e.timestamp).set_key(e.task)
        payload = e.payload.strip()

        if len(payload) == 1:
            item.info.flow, item.info.edge = Task.decode_approach_autonomy(int(payload))
            return item

        if len(payload) == 2:
            item.info.flow = int(payload[0])
            item.info.edge = int(payload[1])
            return item

        if len(payload) == 3 and payload[0] == "0":
            item.info.flow = int(payload[1])
            item.info.edge = int(payload[2])
            return item

        if payload[0] == "{":
            payload = payload[1:-1]
            values = payload.split(",")
            kv: dict[str, str] = {}
            for svalue in values:
                k, v = svalue.split(":")
                kv[k.strip()] = v.strip()

            if "c" in kv:
                item.info.rate = int(kv["c"])
            if "a" in kv:
                item.info.flow = int(kv["a"])
            if "s" in kv:
                item.info.edge = int(kv["s"])
            if "clear" in kv:
                item.info.neat = int(kv["clear"])
            if "fun" in kv:
                item.info.cool = int(kv["fun"])
            if "easy" in kv:
                item.info.easy = int(kv["easy"])
            if "cov" in kv:
                item.info.rate = int(kv["cov"])
            if "app" in kv:
                item.info.flow = int(kv["app"])
            if "aut" in kv:
                item.info.edge = int(kv["aut"])
            return item

        raise Exception(f"Invalid SELF payload: {payload}")

    @staticmethod
    def __convert_to_base_list(e: LogAction) -> LogItemBase | None:

        item: LogItemBase | None = None
        if e.action == AType.PICK.value:
            item = LogItemMove().set_mode(LogItemMove.Mode.PICK).set_timestamp(e.timestamp).set_key(e.task)
        elif e.action == AType.BACK.value:
            item = LogItemMove().set_mode(LogItemMove.Mode.BACK).set_timestamp(e.timestamp).set_key(e.task)
        elif e.action == AType.DOWN.value:
            item = LogItemMove().set_mode(LogItemMove.Mode.DOWN).set_timestamp(e.timestamp).set_key(e.task)
        elif e.action == AType.TEST.value or e.action == AType.PROG.value:
            try:
                rate = int(e.payload)
            except ValueError:
                rate = 0
            item = LogItemExec().set_timestamp(e.timestamp).set_key(e.task)
            if rate != 0:
                item.set_rate(rate)
        elif e.action == AType.FREE.value:
            item = LogItemExec().set_mode(LogItemExec.Mode.FREE).set_timestamp(e.timestamp).set_key(e.task)
        elif e.action == AType.FAIL.value:
            item = LogItemExec().set_fail(LogItemExec.Fail.COMP).set_timestamp(e.timestamp).set_key(e.task)
        elif e.action == AType.SELF.value:
            item = OldLogLoader.decode_self(e)
        return item

    @staticmethod
    def __row_to_action_data( row: list[str]) -> LogAction | None:
        if len(row) < 5:
            return None
        hash = row[0]
        timestamp = row[1]
        action_value = row[2]
        task = row[3]
        payload = row[4]
        return LogAction(hash, timestamp, action_value, task, payload)

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
                action_data = OldLogLoader.__row_to_action_data(row)
                if action_data is not None:
                    entries.append(action_data)
        return entries