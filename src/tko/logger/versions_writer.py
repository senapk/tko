from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import blake2s
from pathlib import Path
from typing import Literal

import base64
import difflib
import gzip
import json
import re
import tempfile


from typing import Any


class InvalidHistoryError(ValueError):
    """A history cannot be safely extended until its invalid entry is repaired."""

    def __init__(self, path: Path, line_number: int, reason: str) -> None:
        self.path: Path = path
        self.line_number: int = line_number
        self.reason: str = reason
        super().__init__(f"{path}:{line_number}: {reason}")


_GIT_CONFLICT_MARKER = re.compile(rb"(?:<{7,}|>{7,}|\|{7,})(?: .*)?|={7,}")


def remove_git_conflict_markers(content: bytes) -> bytes:
    """Remove standalone Git conflict markers while keeping every data line."""
    retained: list[bytes] = []
    for line in content.splitlines(keepends=True):
        if not _GIT_CONFLICT_MARKER.fullmatch(line.rstrip(b"\r\n")):
            retained.append(line)
    return b"".join(retained)


@dataclass(slots=True)
class DiffOp:
    tag: Literal["replace", "insert", "delete"]
    a1: int
    a2: int
    text: str

    def to_dict(self) -> dict[str, object]:
        return {
            "tag": self.tag,
            "a1": self.a1,
            "a2": self.a2,
            "text": self.text,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "DiffOp":
        try:
            tag = str(data["tag"])

            if tag not in { "replace", "insert", "delete" }:
                raise ValueError( f"Invalid diff tag: {tag}" )

            return DiffOp(
                tag=tag, # type: ignore
                a1=int(data["a1"]),
                a2=int(data["a2"]),
                text=str(data["text"]),
            )

        except KeyError as e:
            raise ValueError( f"Missing field: {e.args[0]}" ) from e
        except ( TypeError, ValueError, ) as e:
            raise ValueError( f"Invalid diff operation: {data}" ) from e


@dataclass(slots=True)
class AuditElement:
    timestamp: datetime
    hash_value: str
    mode: Literal["full", "diff"]
    content: str | None = None
    ops: list[DiffOp] | None = None

    def verify_hash(self) -> bool:
        if self.content is None:
            return False
        calculated_hash = blake2s(self.content.encode("utf-8")).hexdigest()
        return calculated_hash == self.hash_value

    def to_jsonl_line(self) -> str:
        entry: dict[str, object] = {
            "ts": int(self.timestamp.timestamp()),
            "hash": self.hash_value,
            "mode": self.mode,
        }

        if self.mode == "full":
            entry["content"] = self.content
        else:
            entry["ops"] = [op.to_dict() for op in self.ops or []]

        return json.dumps(
            entry,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def from_jsonl_line(line: str) -> "AuditElement":
        data = json.loads(line)

        mode = data.get("mode", "full")
        content = data.get("content")

        if mode == "full" and isinstance(content, str):
            try:
                raw = base64.b64decode(content.encode("ascii"))
                content = gzip.decompress(raw).decode("utf-8")
            except Exception:
                # Legacy full snapshots may already be plain text.
                pass

        return AuditElement(
            timestamp=datetime.fromtimestamp(data["ts"]),
            hash_value=data["hash"],
            mode=mode,
            content=content,
            ops=[DiffOp.from_dict(op) for op in data.get("ops", [])]
            if mode == "diff"
            else None,
        )


@dataclass(slots=True)
class VersionSnapshot:
    timestamp: datetime
    hash_value: str
    content: str


@dataclass(slots=True)
class VersionHistory:
    snapshots: list[VersionSnapshot]
    last_full_index: int = 0

    @property
    def current(self) -> str:
        return self.snapshots[-1].content

    @property
    def current_hash(self) -> str:
        return self.snapshots[-1].hash_value

    @property
    def count(self) -> int:
        return len(self.snapshots)


class VersionsWriter:
    def __init__(self, n_diffs: int = 10) -> None:
        self.n_diffs = n_diffs
        self.histories: dict[Path, VersionHistory] = {}

    @staticmethod
    def _compress(content: str) -> str:
        compressed = gzip.compress(content.encode("utf-8"))
        return base64.b64encode(compressed).decode("ascii")

    @staticmethod
    def _decompress(content: str) -> str:
        raw = base64.b64decode(content.encode("ascii"))
        return gzip.decompress(raw).decode("utf-8")

    @staticmethod
    def _hash(content: str) -> str:
        return blake2s(content.encode("utf-8")).hexdigest()

    def _make_diff(
        self,
        old: str,
        new: str,
    ) -> list[DiffOp]:
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)

        matcher = difflib.SequenceMatcher(
            None,
            old_lines,
            new_lines,
        )

        ops: list[DiffOp] = []

        for tag, a1, a2, b1, b2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            ops.append(
                DiffOp(
                    tag=tag,
                    a1=a1,
                    a2=a2,
                    text="".join(new_lines[b1:b2]),
                )
            )

        return ops

    def _apply_diff(
        self,
        content: str,
        ops: list[DiffOp],
    ) -> str:
        lines = content.splitlines(keepends=True)

        result: list[str] = []
        cursor = 0

        for op in ops:
            result.extend(lines[cursor:op.a1])

            if op.tag in ("replace", "insert"):
                result.extend(
                    op.text.splitlines(keepends=True)
                )

            cursor = op.a2

        result.extend(lines[cursor:])

        return "".join(result)

    @staticmethod
    def _replace_history(audit_file: Path, lines: list[bytes]) -> None:
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=audit_file.parent, prefix=f".{audit_file.name}.", delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.writelines(lines)
            temporary_path.chmod(audit_file.stat().st_mode)
            temporary_path.replace(audit_file)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def _load_history(
        self,
        audit_file: Path,
    ) -> VersionHistory:
        snapshots: list[VersionSnapshot] = []
        current = ""
        last_full_index = 0

        if audit_file.exists():
            retained_lines: list[bytes] = []
            removed_markers: bool = False
            for line_number, line in enumerate(
                audit_file.read_bytes().splitlines(keepends=True), start=1
            ):
                if _GIT_CONFLICT_MARKER.fullmatch(line.rstrip(b"\r\n")):
                    removed_markers = True
                    continue
                try:
                    entry = AuditElement.from_jsonl_line(line.decode("utf-8"))
                except (ValueError, KeyError, TypeError, AttributeError, OverflowError) as error:
                    raise InvalidHistoryError(audit_file, line_number, str(error)) from error
                retained_lines.append(line)

                if entry.mode == "full":
                    full_content = entry.content or ""
                    try:
                        current = self._decompress(
                            full_content
                        )
                    except Exception:
                        # Backward compatibility with legacy full snapshots stored as plain text.
                        current = full_content
                    last_full_index = len(snapshots)
                else:
                    current = self._apply_diff(
                        current,
                        entry.ops or [],
                    )

                snapshots.append(
                    VersionSnapshot(
                        timestamp=entry.timestamp,
                        hash_value=entry.hash_value,
                        content=current,
                    )
                )

            if removed_markers:
                # Accept both sides in file order, without deduplication or reserialization.
                # Only replace the file after every retained entry has loaded successfully.
                self._replace_history(audit_file, retained_lines)

        return VersionHistory(
            snapshots=snapshots,
            last_full_index=last_full_index,
        )

    def load_history(
        self,
        audit_file: Path,
    ) -> VersionHistory:
        return self._load_history(audit_file)

    def _history(
        self,
        audit_file: Path,
    ) -> VersionHistory:
        if audit_file not in self.histories:
            self.histories[audit_file] = self.load_history(
                audit_file
            )

        return self.histories[audit_file]

    def write(
        self,
        audit_file: Path,
        content: str,
        timestamp: datetime | None = None,
    ) -> bool:
        history = self._history(audit_file)

        hash_value = self._hash(content)

        if (
            history.snapshots
            and hash_value == history.current_hash
        ):
            return False

        now = timestamp or datetime.now()

        if (
            not history.snapshots
            or len(history.snapshots)
            - history.last_full_index
            >= self.n_diffs
        ):
            entry = AuditElement(
                timestamp=now,
                hash_value=hash_value,
                mode="full",
                content=self._compress(content),
            )

            history.last_full_index = len(
                history.snapshots
            )
        else:
            entry = AuditElement(
                timestamp=now,
                hash_value=hash_value,
                mode="diff",
                ops=self._make_diff(
                    history.current,
                    content,
                ),
            )

        audit_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with audit_file.open(
            "a",
            encoding="utf-8",
        ) as f:
            f.write(entry.to_jsonl_line())
            f.write("\n")

        history.snapshots.append(
            VersionSnapshot(
                timestamp=now,
                hash_value=hash_value,
                content=content,
            )
        )
        return True
