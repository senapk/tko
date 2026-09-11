from __future__ import annotations

from typing import Protocol


class Notifier(Protocol):
    def info(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...


class TextualNotifier:
    """Maps domain feedback to the application-wide Textual toast system."""

    def __init__(self, app: object) -> None:
        self.app = app

    def info(self, message: str) -> None:
        self.app.notify(message, severity="information")  # type: ignore[attr-defined]

    def warning(self, message: str) -> None:
        self.app.notify(message, severity="warning")  # type: ignore[attr-defined]

    def error(self, message: str) -> None:
        self.app.notify(message, severity="error", timeout=8)  # type: ignore[attr-defined]
