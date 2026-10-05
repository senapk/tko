"""Localized terminal output and persistent logs for Git commands."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Protocol

from tko.config.user_data import UserData
from tko.i18n import Msg


def translate(pt: str, en: str) -> str:
    return str(Msg.text(pt=pt, en=en).t())


class SyncReporter(Protocol):
    @property
    def log_file(self) -> Path: ...

    def write(self, message: str = "") -> None: ...
    def step(self, message: str) -> None: ...
    def success(self, message: str) -> None: ...
    def warn(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
    def command(self, command: str) -> None: ...
    def ask(self, prompt: str) -> str: ...
    def confirm(self, prompt: str) -> bool: ...


class SyncConsole:
    def __init__(self, log_file: Path) -> None:
        self.log_file: Path = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def write(self, message: str = "") -> None:
        print(message)
        with self.log_file.open("a", encoding="utf-8") as file:
            file.write(f"{message}\n")

    def step(self, message: str) -> None:
        self.write(f"\n==> {message}")

    def success(self, message: str) -> None:
        self.write(f"[OK] {message}")

    def warn(self, message: str) -> None:
        self.write(f"[{translate('AVISO', 'WARNING')}] {message}")

    def error(self, message: str) -> None:
        self.write(f"[{translate('ERRO', 'ERROR')}] {message}")

    def command(self, command: str) -> None:
        self.write(f"-> {command}")

    def ask(self, prompt: str) -> str:
        return input(prompt)

    def confirm(self, prompt: str) -> bool:
        suffix: str = translate("[S/n] (Enter confirma): ", "[Y/n] (Enter confirms): ")
        answer: str = self.ask(f"{prompt} {suffix}")
        return answer.strip().lower() in {"", "y", "yes", "s", "sim"}


def create_console() -> SyncConsole:
    log_dir: Path = UserData.settings_dir() / "git-sync" / "logs"
    timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    return SyncConsole(log_dir / f"{timestamp}.log")
