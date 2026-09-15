"""Version boundary for persisted task identities (independent of log versions)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import tomllib
from collections.abc import Mapping
from typing import cast

from yaml import YAMLError, safe_load

FORMAT_FILE = "task-format.json"
PENDING_FILE = "migration-pending.json"
FORMAT_VERSION = 5
FORMAT_BYTES = b'{"version": 5}\n'
STATE_FIELDS = frozenset({"selected", "pinned", "expanded"})

type DataValue = str | int | float | bool | None | list[DataValue] | dict[str, DataValue]
type DataDict = dict[str, DataValue]


class MigrationRequiredError(ValueError):
    """Opening this workspace could report incomplete task histories."""


def data_value(value: object) -> DataValue:
    """Validate untyped deserialization at the persistence boundary."""
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, list):
        return [data_value(item) for item in cast(list[object], value)]
    if isinstance(value, Mapping):
        output: DataDict = {}
        for key, item in cast(Mapping[object, object], value).items():
            if not isinstance(key, str):
                raise ValueError("Expected string keys in persisted data")
            output[key] = data_value(item)
        return output
    raise ValueError(f"Unsupported persisted value: {type(value).__name__}")


def read_config(path: Path) -> DataDict:
    content: str = path.read_text(encoding="utf-8")
    try:
        raw: object = safe_load(content) if path.suffix == ".yaml" else tomllib.loads(content)
    except (YAMLError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"Invalid repository configuration: {path}: {exc}") from exc
    parsed: DataValue = data_value(raw)
    if not isinstance(parsed, dict) or not parsed:
        raise ValueError(f"Invalid repository configuration: {path}")
    return parsed


def atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            _ = stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        if os.name == "posix":
            descriptor: int = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def migration_command(root: Path) -> str:
    """Omit the workspace argument when migration can use the current directory."""
    return "tko tool migrate" if root.resolve() == Path.cwd().resolve() else f'tko tool migrate "{root}"'


def require_current_task_data(root: Path) -> None:
    """Run before loading logs; an unversioned empty workspace is still usable."""
    folder: Path = root / ".tko"
    command: str = migration_command(root)
    if (folder / PENDING_FILE).exists():
        raise MigrationRequiredError(f"Migração interrompida. Execute: {command} --recover")
    marker: Path = folder / FORMAT_FILE
    if marker.exists():
        if task_format_version(marker.read_bytes()) == 1:
            raise MigrationRequiredError(f"Pastas de atividades precisam de migração. Execute: {command}")
        if task_format_version(marker.read_bytes()) in {2, 3}:
            raise MigrationRequiredError(f"Dados de tarefas precisam de migração. Execute: {command}")
        if not is_current_format(marker.read_bytes()):
            raise MigrationRequiredError(f"Formato de tarefas não suportado: {marker}")
        return
    for name in ("log", "track", "audit", "history"):
        directory: Path = folder / name
        if directory.exists() and (not directory.is_dir() or any(p.is_file() for p in directory.rglob("*"))):
            raise MigrationRequiredError(f"Dados de tarefas precisam de migração. Execute: {command}")
    for name in ("history.csv", "task_log.csv"):
        if (folder / name).exists():
            raise MigrationRequiredError(f"Dados de tarefas precisam de migração. Execute: {command}")
    if (folder / "repository.yaml").exists():
        raise MigrationRequiredError(f"Configuração antiga precisa de migração. Execute: {command}")
    toml: Path = folder / "repository.toml"
    if toml.is_file():
        config: DataDict = read_config(toml)
        if any(field in config for field in ("sandbox_name", "sandbox_index", "sources", "flags", "lang", "audit", "selected", "selected_index", "pinned", "expanded")):
            raise MigrationRequiredError(f"Configuração antiga precisa de migração. Execute: {command}")
    for name in ("repository.toml", "repository.yaml"):
        path: Path = folder / name
        if not path.exists():
            continue
        config: DataDict = read_config(path)
        state: DataValue = config.get("state", config)
        if isinstance(state, dict) and any(state.get(field) for field in STATE_FIELDS):
            raise MigrationRequiredError(f"Estado de tarefas precisa de migração. Execute: {command}")


def task_format_version(content: bytes) -> int | None:
    try:
        parsed: DataValue = data_value(json.loads(content))
    except (ValueError, UnicodeError):
        return None
    if not isinstance(parsed, dict) or set(parsed) != {"version"}:
        return None
    value: DataValue = parsed["version"]
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def is_current_format(content: bytes) -> bool:
    return task_format_version(content) == FORMAT_VERSION


def initialize_task_data(root: Path) -> None:
    """Mark new, empty workspaces before their first persisted task write."""
    require_current_task_data(root)
    marker: Path = root / ".tko" / FORMAT_FILE
    if not marker.exists():
        atomic_bytes(marker, FORMAT_BYTES)
