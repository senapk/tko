"""Offline migration of task references; never materializes or edits indexes."""
from __future__ import annotations

import csv
import datetime as dt
import io
import json
from pathlib import Path
import re
import tempfile
from collections.abc import Mapping

from tko.feno.task_source import activity_path_from_local_link
from tko.game.quest_parser import QuestParser
from tko.game.task_matcher import TaskMatcher
from tko.logger.log_history import LogHistory
from tko.logger.tracker import Track, load_track_csv, load_track_jsonl
from tko.logger.history import HistoryEvent
from tko.logger.versions_writer import VersionsWriter


def _merge_history_bytes(first: bytes, second: bytes) -> bytes:
    """Merge two independent snapshot histories into one valid diff chain."""
    with tempfile.TemporaryDirectory(prefix="tko-history-merge-") as folder:
        root: Path = Path(folder)
        first_path: Path = root / "first.jsonl"
        second_path: Path = root / "second.jsonl"
        output_path: Path = root / "merged.jsonl"
        first_path.write_bytes(first)
        second_path.write_bytes(second)
        snapshots = VersionsWriter().load_history(first_path).snapshots + VersionsWriter().load_history(second_path).snapshots
        writer: VersionsWriter = VersionsWriter()
        seen: set[tuple[object, str]] = set()
        for snapshot in sorted(snapshots, key=lambda item: item.timestamp):
            identity = (snapshot.timestamp, snapshot.hash_value)
            if identity in seen:
                continue
            seen.add(identity)
            writer.write(output_path, snapshot.content, snapshot.timestamp)
        return output_path.read_bytes()
from tko.repository.remote import Source
from tko.repository.repository_config_migration import canonical_repository_config
from tko.repository.task_data_format import (
    DataDict, DataValue, FORMAT_BYTES, FORMAT_FILE, PENDING_FILE,
    STATE_FIELDS, data_value, read_config, task_format_version,
)
from tko.repository.task_migration_transaction import FileChange, MigrationPlan, persisted_files, safe_path
from tko.repository.task_migration_workspace import plan_activity_moves
from tko.util.git_hub_url import GitHubUrl


def read_mapping(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    raw: DataValue = data_value(json.loads(path.read_bytes()))
    if not isinstance(raw, dict):
        raise ValueError("--map must contain a JSON object of old keys to canonical keys")
    output: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(value, str):
            raise ValueError(f"Invalid mapping value for {key}")
        validate_full_key(value)
        if not key or ("@" in key and key.split("@", 1)[0] != value.split("@", 1)[0]):
            raise ValueError(f"Mapping must preserve the source: {key} -> {value}")
        output[key] = value
    for key, value in output.items():
        if value in output and output[value] != value:
            raise ValueError(f"Chained or cyclic mapping is not supported: {key} -> {value}")
    return output


def validate_full_key(key: str) -> None:
    source, separator, path = key.partition("@")
    if not separator or not source or any(char in source for char in "/\\@") or source in {".", ".."}:
        raise ValueError(f"Invalid task source in key: {key}")
    if "@" in path or "\\" in path or ":" in key or any(ord(char) < 32 for char in key) or ", " in key or key != key.strip():
        raise ValueError(f"Invalid task key: {key}")
    TaskMatcher.validate_key(path)


def _sources(config: DataDict) -> dict[str, Source]:
    output: dict[str, Source] = {}
    profile: DataValue = config.get("profile")
    if isinstance(profile, dict):
        sources: DataValue = profile.get("sources", {})
        if not isinstance(sources, dict):
            raise ValueError("Invalid profile sources")
        for name, entry in sources.items():
            if not isinstance(entry, dict) or not isinstance(entry.get("uri"), str):
                raise ValueError(f"Invalid source: {name}")
            uri: DataValue = entry["uri"]
            assert isinstance(uri, str)
            output[name] = Source.from_uri(name, uri)
        return output
    legacy_sources: DataValue = config.get("sources", [])
    if not isinstance(legacy_sources, list):
        raise ValueError("Invalid legacy sources")
    for entry in legacy_sources:
        if not isinstance(entry, dict):
            raise ValueError("Invalid legacy source")
        source: Source = Source.from_dict(entry)
        output[source.name] = source
    sandbox: DataValue = config.get("sandbox_name")
    index: DataValue = config.get("sandbox_index")
    if isinstance(sandbox, str) and isinstance(index, str):
        output[sandbox] = Source.from_uri(sandbox, index)
    if not output:
        output["labs"] = Source.from_uri("labs", "README.md")
    return output


def _toml_value(value: DataValue) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value).lower()
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{json.dumps(key)} = {_toml_value(item)}" for key, item in value.items()) + " }"
    raise ValueError("TOML cannot represent null")


def _config_bytes(path: Path, data: DataDict) -> bytes:
    # Inline tables preserve all fields, including extensions unknown to RepositoryData.
    text: str = "\n".join(f"{json.dumps(key)} = {_toml_value(value)}" for key, value in data.items()) + "\n"
    return text.encode("utf-8")


class TaskDataMigration:
    def __init__(self, root: Path, mapping: Mapping[str, str] | None = None) -> None:
        self.root: Path = root.resolve()
        self.explicit: dict[str, str] = dict(mapping or {})
        self.plan: MigrationPlan = MigrationPlan(self.root)
        self.candidates: dict[str, set[str]] = {}
        self.canonical: set[str] = set()
        self.tree_keys: set[str] = {""}
        self.activity_paths: dict[str, Path] = {}
        self.source_roots: dict[str, Path] = {}

    def _read(self, path: Path) -> bytes:
        content: bytes = path.read_bytes()
        self.plan.inputs[path] = content
        return content

    def _catalog(self, config: DataDict) -> None:
        for name, source in _sources(config).items():
            validate_full_key(f"{name}@placeholder")
            self.tree_keys.update({name, f"{name}@", f"{name}@_sem_quest"})
            if source.is_git_source:
                github: GitHubUrl | None = GitHubUrl.parse(source.path_or_url)
                if github is None or github.relative_path is None:
                    raise ValueError(f"Invalid source URL: {source.path_or_url}")
                index: Path = self.root / name / github.relative_path
            else:
                index = self.root / source.path_or_url
            if index.is_dir():
                index = index / "README.md"
            self.source_roots[name] = (
                self.root / name if source.is_git_source or not index.resolve().is_relative_to(self.root)
                else index.resolve().parent
            )
            if not index.is_file():
                # Missing/offline indexes can be replaced by explicit mappings.
                continue
            text: str = self._read(index).decode("utf-8-sig")
            for number, line in enumerate(text.splitlines(), 1):
                quest = QuestParser(name).parse_quest(index, line, number)
                if quest is not None:
                    self.tree_keys.add(f"{name}@{quest.basic.key}")
                    continue
                matcher: TaskMatcher = TaskMatcher()
                if not matcher.match_pattern(line):
                    continue
                if matcher.is_url:
                    path: str = matcher.legacy_key or ""
                    if not path:
                        continue
                else:
                    path = activity_path_from_local_link(matcher.link).as_posix()
                key: str = f"{name}@{path}"
                validate_full_key(key)
                self.canonical.add(key)
                self.activity_paths[key] = self.source_roots[name] / path
                self.candidates.setdefault(key, set()).add(key)
                if matcher.legacy_key:
                    old: str = f"{name}@{matcher.legacy_key}"
                    self.candidates.setdefault(old, set()).add(key)

    def _discover_labs_aliases(self) -> None:
        """Register index-backed fallbacks for every persisted reference reader."""
        for destination in sorted(self.canonical):
            source, _, path = destination.partition("@")
            if not path.startswith("labs/"):
                continue
            old: str = f"{source}@{path.removeprefix('labs/')}"
            if old not in self.canonical:
                self.candidates.setdefault(old, set()).add(destination)

    def _labs_destination(self, key: str) -> str | None:
        source, separator, path = key.partition("@")
        if not separator or not source or not path:
            return None
        destination: str = key if path.startswith("labs/") else f"{source}@labs/{path}"
        try:
            validate_full_key(destination)
        except ValueError:
            return None
        self.candidates.setdefault(key, set()).add(destination)
        return destination

    def _resolve(self, key: str, *, state: bool = False) -> str:
        if key == "":
            return key
        if key in self.explicit:
            destination: str = self.explicit[key]
        elif key in self.canonical:
            destination = key
        elif state and key in self.tree_keys:
            return key
        else:
            choices: set[str] = self.candidates.get(key, set())
            if not choices:
                fallback: str | None = self._labs_destination(key)
                if fallback is None:
                    message = f"Unresolved key: {key}; supply --map"
                    if message not in self.plan.errors:
                        self.plan.errors.append(message)
                    return key
                destination = fallback
            elif len(choices) != 1:
                message: str = (
                    f"Ambiguous key: {key} -> {', '.join(sorted(choices))}"
                )
                if message not in self.plan.errors:
                    self.plan.errors.append(message)
                return key
            else:
                destination = next(iter(choices))
        self.plan.mapping[key] = destination
        return destination

    def _log(self, path: Path, content: bytes) -> bytes:
        output: list[str] = []
        for number, line in enumerate(content.decode("utf-8").splitlines(keepends=True), 1):
            if not line.strip():
                output.append(line)
                continue
            try:
                item = LogHistory.decode_line(line)
                if item is None:
                    raise ValueError("Unrecognized log entry")
                matches: list[re.Match[str]] = list(re.finditer(r"(?:^|, )k:([^\r\n]*?)(?=, |\r?$)", line))
                if len(matches) != 1:
                    raise ValueError("Expected exactly one task key")
                match: re.Match[str] = matches[0]
                old: str = match.group(1)
                key: str = self._resolve(old)
                # Keep unknown fields, event version, formatting and timestamps byte-for-byte.
                line = line[:match.start(1)] + key + line[match.end(1):]
            except (ValueError, KeyError, IndexError) as exc:
                self.plan.errors.append(f"{path}:{number}: {exc}")
            output.append(line)
        return "".join(output).encode("utf-8")

    def _csv(self, path: Path, content: bytes) -> bytes:
        if path.name == "task_log.csv":
            self.plan.errors.append(f"Unsupported legacy file: {path}; convert its format before migrating")
            return content
        try:
            rows: list[list[str]] = list(csv.reader(io.StringIO(content.decode("utf-8"), newline=""), strict=True))
        except csv.Error as exc:
            self.plan.errors.append(f"{path}: Invalid CSV: {exc}")
            return content
        changed: bool = False
        for number, row in enumerate(rows, 1):
            if not row:
                continue
            if number == 1 and len(row) >= 4 and row[2].lower() == "action" and row[3].lower() == "task":
                continue
            if len(row) < 5:
                self.plan.errors.append(f"{path}:{number}: Invalid history.csv row")
                continue
            try:
                _ = dt.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.plan.errors.append(f"{path}:{number}: Invalid history.csv timestamp")
                continue
            key: str = self._resolve(row[3])
            changed |= key != row[3]
            row[3] = key
        if not changed:
            return content
        output: io.StringIO = io.StringIO(newline="")
        csv.writer(output).writerows(rows)
        return output.getvalue().encode("utf-8")

    def _state(self, config: DataDict) -> bool:
        changed: bool = False
        states: list[DataDict] = [config]
        nested: DataValue = config.get("state")
        if isinstance(nested, dict):
            states.append(nested)
        for state in states:
            for field in STATE_FIELDS:
                if field not in state:
                    continue
                original: DataValue = state[field]
                if isinstance(original, str):
                    state[field] = self._resolve(original, state=True)
                elif isinstance(original, list) and all(isinstance(item, str) for item in original):
                    state[field] = [self._resolve(item, state=True) for item in original if isinstance(item, str)]
                else:
                    self.plan.errors.append(f"Invalid state field: {field}")
                changed |= state[field] != original
        return changed

    def _history_destination(self, relative: str) -> str:
        parts: tuple[str, ...] = Path(relative).parts
        family: str = parts[1]
        remainder: Path = Path(*parts[2:])
        # Task roots can be nested, so match the longest known identity first.
        roots: dict[str, set[str]] = {}
        for key in self.candidates.keys() | self.explicit.keys():
            if "@" in key:
                source, path = key.split("@", 1)
                prefixes: tuple[str, ...] = (key, f"{source}/{path}")
            else:
                prefixes = (key,)
            for prefix in prefixes:
                roots.setdefault(prefix, set()).add(key)
        matches: list[str] = [prefix for prefix in roots if remainder.as_posix().startswith(prefix + "/")]
        if not matches:
            compact_key: str = remainder.parts[0]
            if "@" in compact_key:
                key = self._resolve(compact_key)
                if "@" in key:
                    source, path = key.split("@", 1)
                    tail = Path(*remainder.parts[1:])
                    return (Path(".tko") / family / source / path / tail).as_posix()
            self.plan.errors.append(f"Unresolved history directory: {relative}; supply --map")
            return relative
        prefix: str = max(matches, key=lambda value: len(Path(value).parts))
        identities: set[str] = roots[prefix]
        if len(identities) != 1:
            self.plan.errors.append(f"Ambiguous history directory: {relative}")
            return relative
        key = self._resolve(next(iter(identities)))
        if "@" not in key:
            return relative
        source, path = key.split("@", 1)
        tail: Path = remainder.relative_to(prefix)
        return (Path(".tko") / family / source / path / tail).as_posix()

    def inspect(self) -> MigrationPlan:
        # Reusing the service starts a fresh inspection.
        self.plan = MigrationPlan(self.root)
        self.candidates.clear()
        self.canonical.clear()
        self.tree_keys = {""}
        self.activity_paths.clear()
        self.source_roots.clear()
        if (self.root / ".tko" / PENDING_FILE).exists():
            raise ValueError("Migração pendente; execute --recover primeiro")
        self.plan.inventory = persisted_files(self.root)
        config_paths: list[Path] = [self.root / ".tko" / name for name in ("repository.toml", "repository.yaml") if (self.root / ".tko" / name).is_file()]
        if not config_paths:
            raise ValueError(f"No TKO configuration found in {self.root}")
        configurations: dict[Path, DataDict] = {}
        for path in config_paths:
            _ = self._read(path)
            configurations[path] = read_config(path)
        self._catalog(configurations[config_paths[0]])
        self._discover_labs_aliases()
        for key, value in self.explicit.items():
            validate_full_key(value)
            if key in self.canonical and key != value:
                self.plan.errors.append(f"Cannot remap an existing canonical task: {key}")
            if "@" in key and key.split("@", 1)[0] != value.split("@", 1)[0]:
                self.plan.errors.append(f"Mapping must preserve the source: {key}")
            if value in self.explicit and self.explicit[value] != value:
                self.plan.errors.append(f"Chained or cyclic mapping: {key}")
            self.candidates.setdefault(value, set()).add(value)

        original: dict[str, bytes] = {}
        desired: dict[str, bytes] = {}
        history_events: dict[str, list[HistoryEvent]] = {}
        unified_history_present: bool = (self.root / ".tko" / "history").is_dir()
        for relative in sorted(self.plan.inventory):
            path = safe_path(self.root, relative)
            content: bytes = self._read(path)
            original[relative] = content
            destination: str = relative
            destination_path: Path = Path(destination)
            if relative.startswith(".tko/log/"):
                if path.suffix != ".log" or path.parent != self.root / ".tko" / "log":
                    self.plan.errors.append(f"Unsupported log file: {relative}")
                else:
                    try:
                        _ = dt.datetime.strptime(path.stem, "%Y-%m-%d")
                    except ValueError:
                        self.plan.errors.append(f"Invalid daily log filename: {relative}")
                    content = self._log(path, content)
            elif relative.startswith((".tko/track/", ".tko/audit/")):
                if unified_history_present:
                    desired[relative] = content
                    continue
                legacy_destination: str = self._history_destination(relative)
                family: str = Path(legacy_destination).parts[1]
                destination_path: Path = Path(".tko") / "history" / Path(*Path(legacy_destination).parts[2:])
                if family == "track" and path.name in {"track.csv", "track.jsonl"}:
                    event_destination: str = destination_path.with_name("events.jsonl").as_posix()
                    try:
                        records: list[Track] = (
                            load_track_csv(content, path) if path.name == "track.csv"
                            else load_track_jsonl(content, path)
                        )
                        history_events.setdefault(event_destination, []).extend(
                            HistoryEvent(
                                record.timestamp,
                                "execution",
                                tuple(item.split(":", 1)[0] for item in record.file_stamp_list),
                                record.result,
                            )
                            for record in records
                        )
                    except ValueError as exc:
                        self.plan.errors.append(str(exc))
                    continue
                if family == "audit":
                    remainder: Path = Path(*destination_path.parts[3:])
                    source_prefix: str = destination_path.parts[2]
                    candidates: list[tuple[int, str, Path]] = []
                    for identity in self.candidates:
                        source, separator, task_path = identity.partition("@")
                        if separator and source == source_prefix:
                            prefix = Path(task_path)
                            if remainder.as_posix().startswith(prefix.as_posix() + "/"):
                                candidates.append((len(prefix.parts), identity, prefix))
                    if candidates:
                        _, _, task_path = max(candidates, key=lambda item: item[0])
                        task_relative: str = remainder.relative_to(task_path).as_posix()
                        event_destination = (Path(".tko") / "history" / source_prefix / task_path / "events.jsonl").as_posix()
                        try:
                            snapshots = VersionsWriter().load_history(path).snapshots
                            history_events.setdefault(event_destination, []).extend(
                                HistoryEvent(snapshot.timestamp.strftime("%Y-%m-%d_%H-%M-%S"), "audit", (task_relative,))
                                for snapshot in snapshots
                            )
                        except (OSError, ValueError):
                            pass
            elif path in configurations:
                if path == config_paths[0]:
                    config: DataDict = configurations[path]
                    _ = self._state(config)
                    try:
                        canonical: DataDict = canonical_repository_config(config)
                        desired[".tko/repository.toml"] = _config_bytes(self.root / ".tko/repository.toml", canonical)
                    except (ValueError, TypeError) as exc:
                        self.plan.errors.append(f"{path}: {exc}")
                # repository.yaml is deleted, including when TOML already takes precedence.
                continue
            elif path.suffix == ".csv":
                content = self._csv(path, content)
            elif path.name == FORMAT_FILE:
                if task_format_version(content) not in {1, 2, 3, 4, 5}:
                    self.plan.errors.append(f"Unsupported task format: {relative}")
            _ = safe_path(self.root, destination)
            if relative.startswith((".tko/track/", ".tko/audit/")):
                destination = destination_path.as_posix()
            if destination in desired and desired[destination] != content and destination.startswith(".tko/history/") and destination.endswith((".json", ".jsonl")):
                # Track and audit used independent history files. Merge their entries
                # into the unified file, rebuilding a valid diff chain.
                try:
                    desired[destination] = _merge_history_bytes(desired[destination], content)
                except (OSError, ValueError):
                    self.plan.errors.append(f"Invalid histories at {destination}; no files will be overwritten")
            elif destination in desired and desired[destination] != content:
                self.plan.errors.append(f"Conflicting histories at {destination}; no files will be overwritten")
            else:
                desired[destination] = content
        for destination, events in history_events.items():
            unique: dict[tuple[str, str, tuple[str, ...], str | None], HistoryEvent] = {
                (event.timestamp, event.kind, event.files, event.result): event for event in events
            }
            desired[destination] = "".join(
                event.to_json_line() for event in sorted(unique.values(), key=lambda item: item.timestamp)
            ).encode("utf-8")
        desired[f".tko/{FORMAT_FILE}"] = FORMAT_BYTES
        for relative in sorted(original.keys() | desired.keys()):
            before: bytes | None = original.get(relative)
            after: bytes | None = desired.get(relative)
            if before != after:
                self.plan.changes.append(FileChange(relative, before, after))
        plan_activity_moves(
            self.plan, self.candidates.keys() | self.explicit.keys(), self.activity_paths,
            self.source_roots, self._resolve,
        )
        return self.plan
