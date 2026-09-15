"""Unified activity history events shared by execution tracking and audit."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from filelock import FileLock

HistoryKind = Literal["audit", "execution"]


@dataclass(frozen=True, slots=True)
class HistoryEvent:
    timestamp: str
    kind: HistoryKind
    files: tuple[str, ...]
    result: str | None = None

    def to_json_line(self) -> str:
        payload: dict[str, object] = {
            "timestamp": self.timestamp,
            "type": self.kind,
            "files": list(self.files),
        }
        if self.result is not None:
            payload["result"] = self.result
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"


def append_event(path: Path, event: HistoryEvent) -> None:
    """Append one event while audit and execution writers may run concurrently."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path.with_name(path.name + ".lock")), timeout=5):
        with path.open("a", encoding="utf-8") as stream:
            _ = stream.write(event.to_json_line())


def event_timestamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%d_%H-%M-%S")
