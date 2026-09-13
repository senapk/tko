import asyncio
from pathlib import Path

import pytest

from tko.config.settings import Settings
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.game.task_resolver import TaskResolver
from tko.ui_textual.app import TkoApp
from tko.ui_textual.dialogs import TextInputDialog


def test_shift_delete_skips_confirmation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings: Settings = Settings(tmp_path)
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)
    task: Task = Task()
    task.basic.key = "example"
    folder: Path = tmp_path / "example"
    folder.mkdir()
    (folder / "answer.py").write_text("# answer\n", encoding="utf-8")

    def selected_task() -> Task:
        return task

    def target_folder(self: TaskResolver, selected: Task) -> Path:
        assert selected is task
        return folder

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None)
        monkeypatch.setattr(app, "_selected_item", selected_task)
        monkeypatch.setattr(TaskResolver, "target_folder", target_folder)
        async with app.run_test() as pilot:
            await pilot.press("delete")
            assert isinstance(app.screen, TextInputDialog)
            assert folder.exists()
            await pilot.click("#cancel")
            await pilot.press("shift+delete")
            assert not isinstance(app.screen, TextInputDialog)
            assert not folder.exists()

    asyncio.run(exercise())
