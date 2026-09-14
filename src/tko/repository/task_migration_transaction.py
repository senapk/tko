"""Recoverable, file-based transaction for the offline task migration."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid

from tko.repository.task_data_format import (
    FORMAT_FILE, PENDING_FILE, DataValue, atomic_bytes, data_value,
)


def digest(content: bytes | None) -> str | None:
    return None if content is None else hashlib.sha256(content).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    path: Path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"Unsafe migration path: {relative}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Migration path escapes workspace: {relative}")
    for parent in (path, *path.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError(f"Symlink in migration path: {parent}")
    return path


@dataclass(frozen=True)
class FileChange:
    relative: str
    before: bytes | None
    after: bytes | None
    before_mode: int | None = None
    after_mode: int | None = None
    before_mtime: int | None = None
    after_mtime: int | None = None


@dataclass(frozen=True)
class DirectoryChange:
    relative: str
    before: int | None
    after: int | None


def tree_entries(root: Path, relative: str) -> set[str]:
    directory: Path = safe_path(root, relative)
    if not directory.exists():
        return set()
    if not directory.is_dir():
        raise ValueError(f"Expected activity directory: {directory}")
    entries: set[str] = {relative + "/"}
    for path in directory.rglob("*"):
        name: str = path.relative_to(root).as_posix()
        _ = safe_path(root, name)
        if path.is_dir():
            entries.add(name + "/")
        elif path.is_file():
            entries.add(name)
        else:
            raise ValueError(f"Unsupported activity file: {path}")
    return entries


def _write_change(root: Path, change: FileChange) -> None:
    path: Path = safe_path(root, change.relative)
    if change.after is None:
        path.unlink(missing_ok=True)
    else:
        atomic_bytes(path, change.after)
        if change.after_mode is not None:
            path.chmod(change.after_mode)
        if change.after_mtime is not None:
            os.utime(path, ns=(change.after_mtime, change.after_mtime))


@dataclass
class MigrationPlan:
    root: Path
    mapping: dict[str, str] = field(default_factory=dict)
    changes: list[FileChange] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    inputs: dict[Path, bytes] = field(default_factory=dict)
    inventory: set[str] = field(default_factory=set)
    trees: dict[str, set[str]] = field(default_factory=dict)
    directories: list[DirectoryChange] = field(default_factory=list)
    moves: dict[str, str] = field(default_factory=dict)

    def apply(self) -> Path | None:
        if self.errors:
            raise ValueError("\n".join(self.errors))
        if (self.root / ".tko" / PENDING_FILE).exists():
            raise ValueError("Migração pendente; execute --recover primeiro")
        if not self.changes and not self.directories:
            return None
        for path, original in self.inputs.items():
            if not path.is_file() or path.read_bytes() != original:
                raise ValueError(f"Input changed since inspection: {path}")
        if persisted_files(self.root) != self.inventory:
            raise ValueError("Workspace changed since inspection; run migration again")
        for relative, expected in self.trees.items():
            if tree_entries(self.root, relative) != expected:
                raise ValueError(f"Activity directory changed since inspection: {relative}")
        for directory in self.directories:
            path = safe_path(self.root, directory.relative)
            if path.exists() and not path.is_dir():
                raise ValueError(f"Activity directory collides with a file: {path}")
            mode: int | None = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
            if mode != directory.before:
                raise ValueError(f"Activity directory changed since inspection: {path}")
        for change in self.changes:
            path: Path = safe_path(self.root, change.relative)
            current: bytes | None = path.read_bytes() if path.is_file() else None
            if current != change.before or (path.exists() and not path.is_file()):
                raise ValueError(f"Destination changed or is not a file: {path}")
            if change.before_mode is not None and stat.S_IMODE(path.stat().st_mode) != change.before_mode:
                raise ValueError(f"File permissions changed since inspection: {path}")
            for parent in path.parents:
                if parent == self.root:
                    break
                if parent.exists() and not parent.is_dir():
                    raise ValueError(f"Destination parent is not a directory: {parent}")

        backup: Path = safe_path(self.root, f".tko/migrations/{uuid.uuid4().hex}")
        entries: list[dict[str, str | int | None]] = []
        for change in self.changes:
            entries.append({"path": change.relative, "before": digest(change.before), "after": digest(change.after),
                            "before_mode": change.before_mode, "after_mode": change.after_mode,
                            "before_mtime": change.before_mtime, "after_mtime": change.after_mtime})
            if change.before is not None:
                atomic_bytes(safe_path(backup / "before", change.relative), change.before)
            if change.after is not None:
                atomic_bytes(safe_path(backup / "after", change.relative), change.after)
        directory_entries: list[dict[str, str | int | None]] = [
            {"path": item.relative, "before": item.before, "after": item.after} for item in self.directories
        ]
        atomic_bytes(backup / "manifest.json", json.dumps({
            "version": 2, "files": entries, "directories": directory_entries,
            "activity_roots": list(self.trees),
        }, indent=2).encode())
        pending: Path = self.root / ".tko" / PENDING_FILE
        atomic_bytes(pending, json.dumps({"backup": backup.relative_to(self.root).as_posix()}).encode())
        # Readers reject the workspace until the final marker and journal removal.
        for directory in sorted(self.directories, key=lambda item: len(Path(item.relative).parts)):
            if directory.after is not None:
                safe_path(self.root, directory.relative).mkdir(parents=True, exist_ok=True)
        marker: FileChange | None = None
        for change in self.changes:
            if change.relative == f".tko/{FORMAT_FILE}":
                marker = change
            else:
                _write_change(self.root, change)
        for directory in sorted(self.directories, key=lambda item: len(Path(item.relative).parts), reverse=True):
            path = safe_path(self.root, directory.relative)
            if directory.after is None:
                path.rmdir()
            else:
                path.chmod(directory.after)
        if marker is not None:
            _write_change(self.root, marker)
        pending.unlink()
        return backup


def persisted_files(root: Path) -> set[str]:
    folder: Path = root / ".tko"
    files: set[str] = set()
    for name in ("log", "track", "audit"):
        directory: Path = safe_path(root, f".tko/{name}")
        if directory.exists() and not directory.is_dir():
            raise ValueError(f"Expected directory: {directory}")
        if directory.is_dir():
            for path in directory.rglob("*"):
                if path.is_symlink():
                    raise ValueError(f"Symlink in persisted history: {path}")
                if path.is_file():
                    files.add(path.relative_to(root).as_posix())
    for name in ("repository.toml", "repository.yaml", "history.csv", "task_log.csv", FORMAT_FILE):
        path = safe_path(root, f".tko/{name}")
        if path.is_file():
            files.add(path.relative_to(root).as_posix())
    return files


def recover_migration(root: Path) -> Path:
    root = root.resolve()
    pending: Path = safe_path(root, f".tko/{PENDING_FILE}")
    raw: DataValue = data_value(json.loads(pending.read_bytes()))
    if not isinstance(raw, dict) or not isinstance(raw.get("backup"), str):
        raise ValueError("Invalid migration journal")
    relative: DataValue = raw["backup"]
    assert isinstance(relative, str)
    if not relative.startswith(".tko/migrations/"):
        raise ValueError("Invalid backup location")
    backup: Path = safe_path(root, relative)
    manifest: DataValue = data_value(json.loads((backup / "manifest.json").read_bytes()))
    if not isinstance(manifest, dict) or manifest.get("version") not in {1, 2}:
        raise ValueError("Invalid migration manifest")
    entries: DataValue = manifest.get("files")
    if not isinstance(entries, list):
        raise ValueError("Invalid migration manifest files")
    roots_value: DataValue = manifest.get("activity_roots", [])
    if not isinstance(roots_value, list) or not all(isinstance(value, str) for value in roots_value):
        raise ValueError("Invalid activity roots in manifest")
    roots: list[Path] = [Path(value) for value in roots_value if isinstance(value, str)]
    for scope in roots:
        if scope == Path(".") or any(part in {".git", ".tko", ".."} for part in scope.parts):
            raise ValueError("Unsafe activity root in manifest")
        _ = safe_path(root, scope.as_posix())

    def allowed(name: str, *, directory: bool = False) -> bool:
        path: Path = Path(name)
        if name.startswith(".tko/") and not directory:
            return True
        return any(path.is_relative_to(scope) or (directory and scope.is_relative_to(path)) for scope in roots)

    directories_value: DataValue = manifest.get("directories", [])
    if not isinstance(directories_value, list):
        raise ValueError("Invalid migration directory list")
    directories: list[DirectoryChange] = []
    for entry in directories_value:
        if not isinstance(entry, dict):
            raise ValueError("Invalid migration directory entry")
        name: DataValue = entry.get("path")
        if not isinstance(name, str) or not allowed(name, directory=True):
            raise ValueError("Invalid migration directory path")
        before: int | None = _optional_int(entry.get("before"))
        after: int | None = _optional_int(entry.get("after"))
        path: Path = safe_path(root, name)
        if path.exists() and not path.is_dir():
            raise ValueError(f"Directory replaced with a file after migration: {path}")
        directories.append(DirectoryChange(name, after, before))
    changes: list[FileChange] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Invalid migration manifest entry")
        name = entry.get("path")
        if not isinstance(name, str) or not allowed(name):
            raise ValueError("Invalid migration file path")
        path = safe_path(root, name)
        if path.exists() and not path.is_file():
            raise ValueError(f"File replaced with a directory after migration: {path}")
        current: bytes | None = path.read_bytes() if path.is_file() else None
        if digest(current) not in (entry.get("before"), entry.get("after")):
            raise ValueError(f"File changed after migration; recovery stopped: {path}")
        original: bytes | None = None
        if entry.get("before") is not None:
            original = safe_path(backup / "before", name).read_bytes()
            if digest(original) != entry["before"]:
                raise ValueError(f"Damaged backup: {name}")
        changes.append(FileChange(
            name, current, original, after_mode=_optional_int(entry.get("before_mode")),
            after_mtime=_optional_int(entry.get("before_mtime")),
        ))
    removable_files: set[str] = {change.relative for change in changes if change.after is None}
    removable_dirs: set[str] = {directory.relative for directory in directories if directory.after is None}
    for name in removable_dirs:
        for node in tree_entries(root, name):
            if node.endswith("/"):
                if node.rstrip("/") not in removable_dirs:
                    raise ValueError(f"Directory added after migration; recovery stopped: {node}")
            elif node not in removable_files:
                raise ValueError(f"File added after migration; recovery stopped: {node}")
    for directory in sorted(directories, key=lambda item: len(Path(item.relative).parts)):
        if directory.after is not None:
            safe_path(root, directory.relative).mkdir(parents=True, exist_ok=True)
    for change in changes:
        _write_change(root, change)
    for directory in sorted(directories, key=lambda item: len(Path(item.relative).parts), reverse=True):
        path = safe_path(root, directory.relative)
        if directory.after is None:
            if path.exists():
                path.rmdir()
        else:
            path.chmod(directory.after)
    pending.unlink()
    return backup


def _optional_int(value: DataValue) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("Invalid file metadata in manifest")
    return value
