import shutil
from datetime import datetime
from pathlib import Path

from tko.repository.repository import Repository
from tko.util.decoder import Decoder


class AuditTracker:
    def __init__(self, repo: Repository, max_file_size_bytes: int = 1024 * 1024):
        self.repo = repo
        self.max_file_size_bytes = max_file_size_bytes

    @staticmethod
    def _format_timestamp(timestamp: datetime) -> str:
        return timestamp.strftime("%Y-%m-%d_%H-%M-%S")

    @staticmethod
    def _to_label(path: Path, task_root: Path) -> str | None:
        try:
            relative_path = path.resolve().relative_to(task_root.resolve())
        except ValueError:
            return None

        if len(relative_path.parts) < 3:
            return None
        if relative_path.parts[0] != "src":
            return None
        return relative_path.as_posix()

    @staticmethod
    def _to_storage_name(timestamp_label: str, file: Path) -> str:
        return f"{timestamp_label}_{file.name}"

    def _should_skip(self, path: Path) -> bool:
        if not path.exists() or not path.is_file():
            return True
        try:
            if path.resolve().is_relative_to(self.repo.paths.config_folder.resolve()):
                return True
        except ValueError:
            pass
        try:
            if path.stat().st_size > self.max_file_size_bytes:
                return True
        except OSError:
            return True
        return False

    def store(self, task_key: str, files: list[Path], timestamp: datetime | None = None) -> tuple[bool, int]:
        audit_task_folder = self.repo.paths.get_audit_task_folder(task_key)
        audit_task_folder.mkdir(parents=True, exist_ok=True)

        if timestamp is None:
            timestamp = datetime.now()
        timestamp_label = self._format_timestamp(timestamp)

        task_root = self.repo.get_task_folder_for_label(task_key)
        any_changes = False
        total_lines = 0

        unique_files = sorted({path.resolve() for path in files})
        for file in unique_files:
            if self._should_skip(file):
                continue

            relative_label = self._to_label(file, task_root)
            if relative_label is None:
                continue

            storage_name = self._to_storage_name(timestamp_label, file)
            output_file = audit_task_folder / storage_name

            try:
                shutil.copy2(file, output_file)
                line_count = len(Decoder.load(file).splitlines())
            except Exception:
                continue

            any_changes = True
            total_lines += line_count

        return any_changes, total_lines
