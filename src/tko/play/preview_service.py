from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from tko.game.task import Task


class PreviewSourceResolver(Protocol):
    def origin_file(self, task: Task, load_git: bool) -> Path | None: ...


@dataclass(frozen=True)
class PreviewResult:
    status: Literal["ready", "select", "unavailable", "unreadable", "empty"]
    markdown: str = ""


class PreviewService:
    """Read original task instructions without materializing or fetching them."""

    def __init__(self, resolver: PreviewSourceResolver) -> None:
        self.resolver: PreviewSourceResolver = resolver

    def load(self, task: Task | None) -> PreviewResult:
        if task is None:
            return PreviewResult("select")
        try:
            path: Path | None = self.resolver.origin_file(task, load_git=False)
            if path is None:
                return PreviewResult("unavailable")
            markdown: str = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return PreviewResult("unavailable")
        except (OSError, UnicodeError):
            return PreviewResult("unreadable")
        if not markdown.strip():
            return PreviewResult("empty")
        return PreviewResult("ready", markdown)
