"""View context shared while browsing student repositories."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReviewContext:
    selected_key: str = ""
    expanded: set[str] = field(default_factory=set)
    view_mode: str = ""
    panel_mode: str = ""
    initialized: bool = False


@dataclass(frozen=True)
class ReviewLocation:
    student: str
    index: int
    total: int


@dataclass(frozen=True)
class ReviewNavigation:
    delta: int


@dataclass(frozen=True)
class ReviewTarget:
    index: int
