"""Minimal contract for resolving a changed file to its current activity."""
from pathlib import Path
from typing import Protocol

from tko.game.task import Task


class TaskPathLookup(Protocol):
    def get_task_from_task_folder(self, folder: Path) -> Task | None: ...
