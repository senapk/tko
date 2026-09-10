from __future__ import annotations

from pathlib import Path
from typing import Literal

from tko.cli.selector import select_with_fzf, select_with_number
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.config.settings import Settings


SelectionMode = Literal["materialized", "downloadable"]


class TaskSelector:
    """Resolve an explicit task, the current task folder, or an interactive choice."""

    def __init__(self, repo: Repository, settings: Settings | None = None):
        self.repo = repo
        self.settings = settings

    def select(
        self,
        pattern: str | None = None,
        use_fzf: bool = False,
        mode: SelectionMode = "materialized",
    ) -> Task | None:
        tasks = self._eligible_tasks(mode)
        if pattern is not None:
            exact = [task for task in tasks if task.basic.full_key == pattern or task.basic.key == pattern]
            if len(exact) == 1:
                return exact[0]

        if pattern is None:
            current = self._current_task(tasks)
            if current is not None:
                return current

        rendered = self._rendered_tasks(tasks)
        items = [(task.basic.full_key, rendered[task.basic.full_key]) for task in tasks]
        if not items:
            return None
        selected = (
            select_with_fzf(items, pattern, selected=self._last_key())
            if use_fzf
            else select_with_number(items, pattern)
        )
        if selected is None:
            return None
        self._save_key(selected)
        return next((task for task in tasks if task.basic.full_key == selected), None)

    def task_folder(self, task: Task) -> Path:
        if task.location.is_external:
            folder = self.repo.task_resolver.target_folder(task)
            if folder is not None:
                return folder.resolve()
        return (task.location.index_path.parent / task.location.raw_link).resolve().parent

    def is_materialized(self, task: Task) -> bool:
        folder = self.task_folder(task)
        return folder.is_dir() and (folder / "README.md").is_file()

    def _eligible_tasks(self, mode: SelectionMode) -> list[Task]:
        tasks = list(self.repo.game.tasks.values())
        if mode == "downloadable":
            return [task for task in tasks if task.location.is_external and not self.is_materialized(task)]
        return [task for task in tasks if self.is_materialized(task)]

    def _current_task(self, tasks: list[Task]) -> Task | None:
        current = Path.cwd().resolve()
        matches = [task for task in tasks if current.is_relative_to(self.task_folder(task))]
        return matches[0] if len(matches) == 1 else None

    def _rendered_tasks(self, tasks: list[Task]) -> dict[str, str]:
        fallback = {task.basic.full_key: f"{task.basic.full_key}  {task.basic.title}" for task in tasks}
        if self.settings is None:
            return fallback

        from tko.cmds.cmd_open import CmdOpen

        tree = CmdOpen(self.settings, self.repo).build_tree(show_all=True, full_key=False, quests_keys=True)
        rendered: dict[str, str] = {}
        for item, tree_item in tree.get_rendered_items(show_selected=False):
            if isinstance(tree_item, Task) and tree_item.basic.full_key in fallback:
                rendered[tree_item.basic.full_key] = (
                    item.plain() if self.settings.rs.monochrome else item.ansi()
                )
        return {key: rendered.get(key, value) for key, value in fallback.items()}

    def _last_key(self) -> str | None:
        path = self.repo.paths.root_dir / ".tko" / ".fzf"
        return path.read_text(encoding="utf-8").strip() if path.exists() else None

    def _save_key(self, key: str) -> None:
        path = self.repo.paths.root_dir / ".tko" / ".fzf"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(key, encoding="utf-8")
