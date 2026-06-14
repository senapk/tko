from __future__ import annotations
from pathlib import Path
from datetime import datetime
from pathlib import Path

from filelock import FileLock, Timeout
from loguru import logger
from tko.repository.repository import Repository
from tko.util.decoder import Decoder
from hashlib import blake2s
import json
from tko.util.console import Console
from tko.util.rt import RT

class AuditElement:
    def __init__(self, timestamp: datetime, hash_value: str, content: str):
        self.timestamp = timestamp
        self.hash_value = hash_value
        self.content = content

    def to_jsonl_line(self) -> str:
        entry: dict[str, object] = {
            "ts": int(self.timestamp.timestamp()),
            "label": self.timestamp.strftime("%Y/%m/%d-%H:%M:%S"),
            "hash": self.hash_value,
            "content": self.content,
        }
        return json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
    
    def verify_hash(self) -> bool:
        calculated_hash = blake2s(self.content.encode("utf-8")).hexdigest()
        return calculated_hash == self.hash_value

    @staticmethod
    def from_jsonl_line(jsonl_line: str) -> AuditElement:
        try:
            entry = json.loads(jsonl_line)
            timestamp = datetime.fromtimestamp(entry["ts"])
            hash_value = entry["hash"]
            content = entry["content"]
            return AuditElement(timestamp, hash_value, content)
        except Exception as e:
            logger.warning(f"Failed to parse jsonl line: {e}")
            raise ValueError("Invalid jsonl line format") from e
        
    

class AuditTracker:
    def __init__(self, repo: Repository, verbose: bool, interval_seconds: int, max_file_size_bytes: int = 1024 * 1024):
        self.repo = repo
        self.max_file_size_bytes = max_file_size_bytes
        self.verbose = verbose
        self.interval_seconds = interval_seconds


    def _is_auditable(self, path: Path, task_root: Path) -> bool:
        if not path.exists() or not path.is_file():
            return False
        try:
            if path.stat().st_size > self.max_file_size_bytes:
                return False
        except OSError:
            return False
        try:
            relative_path = path.resolve().relative_to(task_root.resolve())
        except ValueError:
            return False
        if len(relative_path.parts) < 3:
            return False
        if path.parent.parent.name != "src":
            return False
        if path.suffix in [".exe", ".bin", ".out"]:
            return False
        return True

    @staticmethod
    def _output_file_last(file: Path) -> Path:
        return file.with_name(file.name + ".last")
    
    @staticmethod
    def _task_lock_file(task_dir: Path) -> Path:
        return task_dir / "watcher.lock"

    @staticmethod
    def _to_storage_name(timestamp_label: str, file: Path) -> str:
        return f"{timestamp_label}_{file.name}"

    def _read_last_content(self, audit_last_file: Path) -> tuple[datetime | None, str | None]:
        if not audit_last_file.exists():
            return None, None
        try:
            with audit_last_file.open("r", encoding="utf-8") as f:
                last_content = f.read()
            last_entry = json.loads(last_content)
            last_timestamp = datetime.fromtimestamp(last_entry["ts"])
            last_hash = last_entry["hash"]
            return last_timestamp, last_hash
        except Exception as e:
            logger.warning(f"Failed to read last content from {audit_last_file}: {e}")
            return None, None
        
    @staticmethod
    def _generate_last_content(timestamp: datetime, hash_value: str) -> str:
        entry: dict[str, object] = {
            "ts": int(timestamp.timestamp()),
            "hash": hash_value,
        }
        return json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
    
    def _is_too_soon(self, audit_last_file: Path, new_timestamp: datetime, new_hash: str) -> bool:
        ts_last, hash_last = self._read_last_content(audit_last_file)
        if ts_last is not None and hash_last is not None:
            if new_timestamp.timestamp() - ts_last.timestamp() < self.interval_seconds:
                return True
            if new_hash == hash_last:
                return True
        return False

    def store(self, task_key: str, file_ts_list: list[tuple[Path, datetime | None]]) -> tuple[bool, int]:
        audit_task_folder = self.repo.paths.get_audit_task_folder(task_key)
        audit_task_folder.mkdir(parents=True, exist_ok=True)

        task_root = self.repo.get_task_folder_for_label(task_key)
        any_changes = False
        total_lines = 0

        resolved_files = [(file.resolve(), ts) for file, ts in file_ts_list]
        audit_task_lock_file = self._task_lock_file(audit_task_folder)
        lock = FileLock(str(audit_task_lock_file), timeout=1)
        try:
            for file, ts in resolved_files:
                if ts is None:
                    ts = datetime.now()
                with lock:
                    changed, line_count = self.save_file(file, task_root, audit_task_folder, task_key, ts)
                if changed:
                    any_changes = any_changes or changed
                    total_lines += line_count
        except Timeout:
            logger.warning(f"[audit] Could not acquire lock for task {task_key}, skipping this cycle.")
            return False, 0

        return any_changes, total_lines

    def save_file(self, file: Path, task_root: Path, audit_task_folder: Path, task_key: str, timestamp: datetime) -> tuple[bool, int]:
        logger.debug(f"Attempting to save file {file} for task {task_key} at {timestamp}")
        if not self._is_auditable(file, task_root):
            return False, 0

        # calculate hash of the file content
        content = Decoder.load(file)
        hash_value = blake2s(content.encode("utf-8")).hexdigest()
        output_file = audit_task_folder / (file.name + ".jsonl")
        
        # verify changes in concurrent scenarios using .last file
        audit_last_file = self._output_file_last(output_file)
        if self._is_too_soon(audit_last_file, timestamp, hash_value):
            logger.debug(f"Change for file {file} is too soon or has same content, skipping save.")
            return False, 0

        try:
            jsonl_line = AuditElement(timestamp, hash_value, content).to_jsonl_line()
            with output_file.open("a", encoding="utf-8") as f:
                f.write(jsonl_line + "\n")
            
            last_content = self._generate_last_content(timestamp, hash_value)
            with audit_last_file.open("w", encoding="utf-8") as f:
                f.write(last_content)

            line_count = len(content.splitlines())
        except Exception as e:
            logger.warning(f"Failed to process file {file}: {e}")
            return False, 0

        logger.debug(f"Sending to console: {file} with verbose {self.verbose}")
        if self.verbose:
            hh_mm_ss = timestamp.strftime("%H:%M:%S")
            Console.print(RT.parse(f"[y][[audit]][] {hh_mm_ss} {task_key}"), flush=True)

        return True, line_count