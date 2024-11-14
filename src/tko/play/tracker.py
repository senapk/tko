import datetime
import os
import argparse
import csv
from tko.play.patch_history import PatchHistory
from tko.util.decoder import Decoder

class Track:
    def __init__(self):
        self.timestamp = ""
        self.files: list[str] = []
        self.result: str = ""

    def set_timestamp(self, timestamp: str):
        self.timestamp = timestamp
        return self
    
    def set_files(self, files: list[str]):
        self.files = [os.path.basename(f) for f in files]
        return self
    
    def set_result(self, result: str):
        self.result = result
        return self
    
    def track_to_column(self):
        return [self.timestamp, self.result, ";".join(self.files)]


class Tracker:

    def __init__(self):
        self._files: list[str] = []
        self._folder: str = ""
        self._result: str = "None"
        self.log_file = "track.csv"
        self.track_folder = ".track"
        self.extension = ".json"

    def set_files(self, files: list[str]):
        self._files = [os.path.abspath(f) for f in files]
        return self
    
    def set_result(self, result: str):
        self._result = result
        return self
    
    def set_percentage(self, percentage: int):
        self._result = "{}%".format(str(percentage).rjust(3, "0"))
        return self

    def get_log_full_path(self):
        return os.path.join(self._folder, self.log_file)

    def set_folder(self, folder: str):
        self._folder = folder
        return self
    
    # in format: YYYY-MM-DD HH:MM:SS
    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # return timestamp of the last version of the file
    def save_file_with_timestamp_prefix(self, timestamp: str, file: str) -> str:
        filename = os.path.basename(file)
        ph = PatchHistory()
        json_file = os.path.join(self._folder, f"{filename}{self.extension}")
        ph.set_json_file(json_file)
        ph.load_json()

        content = Decoder.load(file)
        last_version = ph.store_version(timestamp, content)
        if last_version == timestamp:
            ph.save_json()
            return timestamp
        return last_version

    def store(self):
        os.makedirs(self._folder, exist_ok=True)
        file_list = os.listdir(self._folder)
        file_list = [f for f in file_list if f.endswith(self.extension)]

        files_in_this_version: list[str] = []
        timestamp = self.get_timestamp()

        for file in self._files:
            stored = self.save_file_with_timestamp_prefix(timestamp, file)
            filename = os.path.basename(file)
            files_in_this_version.append(filename + ":" + stored)

        log_file = self.get_log_full_path()
        track = Track().set_timestamp(timestamp).set_files(files_in_this_version).set_result(self._result)
        with open(log_file, encoding="utf-8", mode="a") as f:
            writer = csv.writer(f)
            writer.writerow(track.track_to_column())

    @staticmethod
    def main():
        parser = argparse.ArgumentParser(description="Track files changes.")
        parser.add_argument("files", metavar="files", type=str, nargs="+", help="files to be tracked.")
        args = parser.parse_args()
        
        tracker = Tracker().set_folder(".track").set_files(args.files)
        tracker.store()
