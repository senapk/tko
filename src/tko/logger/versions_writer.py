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


from typing import Any


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

    def _load_history(
        self,
        audit_file: Path,
    ) -> VersionHistory:
        snapshots: list[VersionSnapshot] = []
        current = ""
        last_full_index = 0

        if audit_file.exists():
            for line in audit_file.read_text(
                encoding="utf-8"
            ).splitlines():
                entry = AuditElement.from_jsonl_line(line)

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
    ) -> None:
        history = self._history(audit_file)

        hash_value = self._hash(content)

        if (
            history.snapshots
            and hash_value == history.current_hash
        ):
            return

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
