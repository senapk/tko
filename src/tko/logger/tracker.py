from __future__ import annotations

import datetime
import os
import argparse
import csv
import io
import json
from collections.abc import Callable
from pathlib import Path
from typing import Literal, cast
from tko.logger.patch_history import PatchHistory, PatchInfo
from tko.logger.versions_writer import InvalidHistoryError, VersionsWriter
from tko.i18n import Msg
from tko.util.decoder import Decoder
import tempfile
from tko.logger.log_sort import LogSort
from tko.util.console import Console
from tko.logger.history import HistoryEvent, append_event


_TRACKER_NOT_ENOUGH_COLUMNS = Msg.text(
    pt="Colunas insuficientes para criar um objeto Track.",
    en="Not enough columns to create a Track object.",
)
_TRACKER_INVALID_TIMESTAMP_FORMAT = Msg.text(
    pt="Formato de timestamp inválido: {timestamp}. O formato esperado é YYYY-MM-DD_HH-MM-SS.",
    en="Invalid timestamp format: {timestamp}. Expected format is YYYY-MM-DD_HH-MM-SS.",
)
_TRACKER_INVALID_HISTORY = Msg.text(
    pt="Aviso: versão não salva. Histórico inválido em {error}. Corrija o histórico (resolva eventuais conflitos Git) para voltar a salvar versões. O arquivo foi preservado.",
    en="Warning: version not saved. Invalid history at {error}. Repair the history (resolve any Git conflicts) to resume saving versions. The file was preserved.",
)

class Track:
    def __init__(self) -> None:
        self.timestamp: str = ""
        self.file_stamp_list: list[str] = []
        self.result: str = ""

    def set_timestamp(self, timestamp: str) -> Track:
        self.timestamp = timestamp
        return self
    
    def set_file_stamp_list(self, files: list[str]) -> Track:
        self.file_stamp_list = list(files)
        return self
    
    def set_result(self, result: str) -> Track:
        self.result = result
        return self
    
    def track_to_column(self) -> list[str]:
        return [self.timestamp, self.result, ";".join(self.file_stamp_list)]

    def column_to_track(self, columns: list[str]) -> Track:
        if len(columns) < 3:
            raise ValueError(_TRACKER_NOT_ENOUGH_COLUMNS.t())
        self.timestamp = columns[0]
        self.result = columns[1]
        self.file_stamp_list = columns[2].split(";") if columns[2] else []
        return self

    def identity(self) -> tuple[str, str, tuple[str, ...]]:
        return self.timestamp, self.result, tuple(self.file_stamp_list)

    def to_json_line(self) -> str:
        return json.dumps(
            {"timestamp": self.timestamp, "result": self.result, "files": self.file_stamp_list},
            ensure_ascii=False, separators=(",", ":"),
        ) + "\n"

    @classmethod
    def from_json_line(cls, line: str) -> Track:
        payload: object = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object")
        record: dict[object, object] = cast(dict[object, object], payload)
        if set(record) != {"timestamp", "result", "files"}:
            raise ValueError("Expected timestamp, result and files")
        timestamp: object = record["timestamp"]
        result: object = record["result"]
        files: object = record["files"]
        if not isinstance(timestamp, str) or not isinstance(result, str) or not isinstance(files, list):
            raise ValueError("Invalid track record field types")
        file_list: list[object] = cast(list[object], files)
        if not all(isinstance(file, str) for file in file_list):
            raise ValueError("Invalid track file list")
        _ = Tracker.get_timestamp_from_string(timestamp)
        return cls().set_timestamp(timestamp).set_result(result).set_file_stamp_list(
            [file for file in file_list if isinstance(file, str)]
        )


def load_track_jsonl(content: bytes, path: Path) -> list[Track]:
    tracks: list[Track] = []
    try:
        lines: list[str] = content.decode("utf-8").splitlines()
    except UnicodeError as exc:
        raise ValueError(f"{path}:1: Invalid track JSONL encoding: {exc}") from exc
    for number, line in enumerate(lines, 1):
        try:
            tracks.append(Track.from_json_line(line))
        except (ValueError, UnicodeError) as exc:
            raise ValueError(f"{path}:{number}: Invalid track JSONL: {exc}") from exc
    return tracks


def load_track_csv(content: bytes, path: Path) -> list[Track]:
    tracks: list[Track] = []
    try:
        source: str = content.decode("utf-8")
    except UnicodeError as exc:
        raise ValueError(f"{path}:1: Invalid track CSV encoding: {exc}") from exc
    reader = csv.reader(io.StringIO(source, newline=""), strict=True)
    try:
        for row in reader:
            number: int = reader.line_num
            if len(row) != 3:
                raise ValueError(f"{path}:{number}: Expected three track CSV columns")
            track: Track = Track().column_to_track(row)
            try:
                _ = Tracker.get_timestamp_from_string(track.timestamp)
            except ValueError as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
            tracks.append(track)
    except csv.Error as exc:
        raise ValueError(f"{path}:{reader.line_num}: Invalid track CSV: {exc}") from exc
    return tracks


class Tracker:
    log_file = "track.jsonl"
    extension = ".jsonl"

    def __init__(self, on_warning: Callable[[str], None] | None = None) -> None:
        self._result: str = "None"
        self._files: list[Path] = []
        self._folder: Path = Path()
        self._task_root: Path | None = None
        self._versions_writer: VersionsWriter = VersionsWriter()
        self._on_warning: Callable[[str], None] = on_warning or self._print_warning
        self._event_folder: Path | None = None
        self._event_type: Literal["audit", "execution"] = "execution"

    @staticmethod
    def _print_warning(message: str) -> None:
        Console.error(message)

    def unfold_files(self, log_sort: LogSort) -> tuple[str, str]:
        output = "\n"
        timestamp_rate: dict[str, str] = {}
        exec_list = log_sort.exec_list
        for _, item in exec_list:
            timestamp = item.get_timestamp().replace(":", "-").replace(" ", "_")
            timestamp_rate[timestamp] = str(item.rate)

        # tracks: list[Track] = Tracker.load_from_log(self.log_file)
        # for track in tracks:
        #     for file in track.file_stamp_list:
        #         file_dict[file] = track.result

        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            for path in self._folder.rglob("*"):
                if not path.is_file() or path.name == self.log_file:
                    continue
                if path.suffix not in {".json", ".jsonl"}:
                    continue
                if path.suffix == ".jsonl":
                    complete = [
                        PatchInfo(
                            snapshot.timestamp.strftime("%Y-%m-%d_%H-%M-%S"),
                            snapshot.content,
                        )
                        for snapshot in VersionsWriter().load_history(Path(path)).snapshots
                    ]
                    filename = path.relative_to(self._folder).as_posix()[:-len(".jsonl")].replace("/", "__")
                else:
                    ph = PatchHistory().set_json_file(path.as_posix()).load_json()
                    complete = ph.restore_all()
                    filename = path.relative_to(self._folder).as_posix()[:-len(".json")].replace("/", "__")
                for i, patch in enumerate(complete):
                    key = patch.label
                    rate = timestamp_rate.get(key, "000")
                    try:
                        if int(rate) < 0:
                            rate = "0"
                    except ValueError as _:
                        pass
                    result = rate.rjust(3, "0")
                    output_file = os.path.join(temp_dir, f"{patch.label}__rate-{result}__{filename}")
                    if i < 5 or i == len(complete) - 1:
                        output += f"  Extraindo: {output_file}\n"
                    elif i == 5:
                        output += "...\n"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(patch.content)
            output += f"\nPasta com os arquivos: {temp_dir}\n"
            return output, temp_dir


    def set_files(self, files: list[Path]) -> Tracker:
        self._files = files
        return self
    
    def set_result(self, result: str) -> Tracker:
        self._result = result
        return self
    
    def set_percentage(self, percentage: int) -> Tracker:
        self._result = "{}%".format(str(percentage).rjust(3, "0"))
        return self

    def get_log_full_path(self) -> str:
        return os.path.join(self._folder, Tracker.log_file)

    def set_folder(self, folder: Path) -> Tracker:
        self._folder = folder
        return self

    def set_event_folder(self, folder: Path) -> Tracker:
        self._event_folder = folder
        return self

    def set_event_type(self, event_type: Literal["audit", "execution"]) -> Tracker:
        self._event_type = event_type
        return self

    def set_task_root(self, task_root: Path) -> Tracker:
        self._task_root = task_root
        return self

    def _relative_file(self, file: Path) -> Path:
        if self._task_root is not None:
            try:
                return file.resolve().relative_to(self._task_root.resolve())
            except ValueError:
                pass
        return Path(file.name)
    
    # in format: YYYY-MM-DD HH:MM:SS
    @staticmethod
    def get_timestamp() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    @staticmethod
    def get_timestamp_from_string(timestamp: str) -> datetime.datetime:
        try:
            return datetime.datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")
        except ValueError:
            raise ValueError(str(_TRACKER_INVALID_TIMESTAMP_FORMAT).format(timestamp=timestamp))

    # return timestamp of the last version of the file
    def save_file_with_timestamp_prefix(self, timestamp: str, file: Path) -> tuple[str, bool, int]:
        relative = self._relative_file(file)
        json_file = self._folder / relative.with_name(relative.name + Tracker.extension)
        json_file.parent.mkdir(parents=True, exist_ok=True)

        content = Decoder.load(file)
        changed = self._versions_writer.write(
            audit_file=Path(json_file),
            content=content,
            timestamp=self.get_timestamp_from_string(timestamp),
        )
        if changed:
            return timestamp, True, len(content.splitlines())

        history = self._versions_writer.load_history(Path(json_file))
        if history.snapshots:
            last_version = history.snapshots[-1].timestamp.strftime("%Y-%m-%d_%H-%M-%S")
            return last_version, False, len(content.splitlines())
        return timestamp, False, len(content.splitlines())

    # return True if any file was changed
    def store(self) -> tuple[bool, int]:
        os.makedirs(self._folder, exist_ok=True)

        files_in_this_version: list[str] = []
        timestamp = self.get_timestamp()

        any_changes = False
        total_size = 0
        for file in self._files:
            try:
                stored, changed, size = self.save_file_with_timestamp_prefix(timestamp, file)
            except InvalidHistoryError as error:
                self._on_warning(_TRACKER_INVALID_HISTORY.t().format(error=error).plain())
                continue
            total_size += size
            filename = self._relative_file(file).as_posix()
            files_in_this_version.append(filename + ":" + stored)
            if changed:
                any_changes = True

        track = Track().set_timestamp(timestamp).set_file_stamp_list(files_in_this_version).set_result(self._result)
        if self._event_folder is not None:
            event_files = tuple(item.split(":", 1)[0] for item in files_in_this_version)
            append_event(
                self._event_folder / "events.jsonl",
                HistoryEvent(timestamp, self._event_type, event_files, self._result if self._event_type == "execution" else None),
            )
        else:
            log_file = self.get_log_full_path()
            with open(log_file, encoding="utf-8", mode="a", newline="") as f:
                _ = f.write(track.to_json_line())
        return any_changes, total_size
    
    @staticmethod
    def load_from_log(log_file: str) -> list[Track]:
        if not os.path.exists(log_file):
            return []
        
        return load_track_jsonl(Path(log_file).read_bytes(), Path(log_file))

    @staticmethod
    def main() -> None:
        parser = argparse.ArgumentParser(description="Track files changes.")
        parser.add_argument("files", metavar="files", type=str, nargs="+", help="files to be tracked.")
        args = parser.parse_args()
        
        tracker = Tracker().set_folder(Path(".track")).set_files(args.files)
        tracker.store()
