from tko.game.task import Task

from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_move import LogItemMove
from tko.logger.log_item_self import LogItemSelf
from tko.play.patch_history import PatchHistory, PatchInfo
from tko.play.tracker import Tracker, Track
from tko.settings.rep_paths import RepPaths
from tko.util.decoder import Decoder
import enum
import csv
import os
from icecream import ic

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


class TrackerLoader:
    @staticmethod
    def load_file_versions(task_track_folder: str) -> dict[str, dict[str, PatchInfo]]:
        files: list[str] = os.listdir(task_track_folder)
        files = [f for f in files if f.endswith(Tracker.extension)]
        file_versions: dict[str, dict[str, PatchInfo]] = {}
        for f in files:
            file_name = f[:-len(Tracker.extension)]
            file_path = os.path.join(task_track_folder, f)
            if not os.path.isfile(file_path):
                continue
            try:
                patch_history: list[PatchInfo] = PatchHistory().set_json_file(file_path).load_json().restore_all()
                file_versions[file_name] = {}
                for patch in patch_history:
                    file_versions[file_name][patch.label] = patch
            except Exception as e:
                print(f"Error loading patch history from {file_path}: {e}")
        return file_versions

    @staticmethod
    def load_track_csv(task_track_folder: str) -> list[Track]:
        csv_file = os.path.join(task_track_folder, "track.csv")
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} does not exist.")
            return []
        return Tracker.load_from_log(csv_file)

    @staticmethod
    def load_from_task_track(task_track_folder: str) -> dict[str, LogItemExec]:
        task = os.path.basename(task_track_folder)
        tracks: list[Track] = TrackerLoader.load_track_csv(task_track_folder)
        file_versions: dict[str, dict[str, PatchInfo]] = TrackerLoader.load_file_versions(task_track_folder)
        output: dict[str, LogItemExec] = {}
        for track in tracks:
            track_datetime = Tracker.get_timestamp_from_string(track.timestamp)

            item = LogItemExec().set_datetime(track_datetime).set_key(task)
            rate = 0
            try:
                rate = int(track.result[:-1])  # Remove '%' and convert to int
            except ValueError:
                pass
            item.set_rate(rate)
            lines = 0
            for file_stamp in track.file_stamp_list:
                file, stamp = file_stamp.split(":")
                if file in file_versions:
                    if stamp in file_versions[file]:
                        patch_info = file_versions[file][stamp]
                        lines += patch_info.lines
            item.set_size(True, lines)
            output[item.get_timestamp()] = item
        return output

class OldLogLoader:
    def __init__(self, rep_folder: str):
        self.rep_folder = rep_folder
        self.paths = RepPaths(rep_folder)
        self.base_list: list[LogItemBase] = []
        self.base_dict: dict[str, LogItemBase] = {}

        self.merge_old_log_into_base()
        self.merge_track_into_base()

        # with open("log2.txt", "w", encoding="utf-8") as log_file:
        #     for key, item in self.base_dict.items():
        #         log_file.write(f"{key}: {item.encode_line()}\n")

    def merge_old_log_into_base(self):
        old_log_file = self.paths.get_old_history_file()
        entries: list[LogAction] = OldLogLoader.__load_file(old_log_file)
        for e in entries:
            item = OldLogLoader.__convert_to_base_list(e)
            if item is not None:
                self.base_list.append(item)
                key = item.get_timestamp().replace(" ", "_").replace(":", "-")
                self.base_dict[key] = item

    def merge_track_into_base(self) -> None:
        track_exec_list: dict[str, LogItemExec] = self.load_from_track_folder()
        for time, item_from_track in track_exec_list.items():
            done: bool = False
            if time in self.base_dict:
                item = self.base_dict[time]
                if isinstance(item, LogItemExec):
                    item_exec: LogItemExec = item
                    item_exec.set_size(True, item_from_track.get_size())
                    done = True
            if not done:
                item_exec = LogItemExec().set_timestamp(time).set_key(item_from_track.get_key())
                item_exec.set_rate(item_from_track.get_rate())
                item_exec.set_size(True, item_from_track.get_size())
                self.base_list.append(item_exec)
                self.base_dict[time] = item_exec        

    def load_from_track_folder(self) -> dict[str, LogItemExec]:
        output: dict[str, LogItemExec] = {}
        track_folder = self.paths.get_track_folder()
        if not os.path.exists(track_folder):
            return output
        entries = os.listdir(track_folder)
        for e in entries:
            folder_path = os.path.join(track_folder, e)
            if not os.path.isdir(folder_path):
                continue
            dict_stamp_exec: dict[str, LogItemExec] = TrackerLoader.load_from_task_track(folder_path)
            output.update(dict_stamp_exec)

        return output
            

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
