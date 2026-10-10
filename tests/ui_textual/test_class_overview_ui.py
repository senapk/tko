"""The class table opens a student while retaining the compared task."""

from __future__ import annotations

import asyncio
import csv
from pathlib import Path

from pytest import MonkeyPatch
from textual.widgets import DataTable, Input

from tko.config.settings import Settings
from tko.game.quest import Quest
from tko.game.task import Task
from tko.play.review_context import ReviewContext, ReviewLocation, ReviewTarget
from tko.play.review_overview import ReviewOverviewService, ReviewTaskRow
from tko.repository.repository import Repository
from tko.ui_textual.app import TkoApp
from tko.ui_textual.review_overview import ReviewOverviewScreen
from tko.ui_textual.dialogs import TextInputDialog


def test_class_table_opens_selected_student(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    folders: list[Path] = [tmp_path / "alice", tmp_path / "bob"]
    for folder in folders:
        folder.mkdir()
    settings: Settings = Settings(tmp_path / "settings")
    settings.get_settings_dir().mkdir(parents=True, exist_ok=True)
    repo: Repository = Repository(folders[0], settings.rs, None, recursive_search=False)
    quest: Quest = Quest("Quest", "quest")
    quest.basic.source_name = "course"
    task: Task = Task()
    task.basic.source_name = "course"
    task.basic.key = "plan/task"
    task.basic.title = "Task"
    task.quest_key = quest.basic.full_key
    quest.add_task(task)
    repo.game.quests = {quest.basic.full_key: quest}
    repo.game.ordered_quests = [quest.basic.full_key]
    repo.game.tasks = {task.basic.full_key: task}
    service: ReviewOverviewService = ReviewOverviewService(folders, settings.rs)

    def row(_task_key: str, index: int, *, refresh: bool = False) -> ReviewTaskRow:
        _ = refresh
        return ReviewTaskRow(index, folders[index].name, folders[index], "sem atividade")

    monkeypatch.setattr(service, "row", row)
    context: ReviewContext = ReviewContext(
        selected_key=task.basic.full_key, expanded={quest.basic.full_key},
        view_mode="all", initialized=True,
    )

    async def exercise() -> None:
        app: TkoApp = TkoApp(
            settings, repo, None, review_context=context,
            review_location=ReviewLocation("alice", 0, 2), review_overview=service,
        )
        async with app.run_test() as pilot:
            await pilot.press("m")
            await pilot.pause()
            assert isinstance(app.screen, ReviewOverviewScreen)
            overview: ReviewOverviewScreen = app.screen
            table: DataTable[str] = overview.query_one(DataTable)
            assert overview.task_key == task.basic.full_key
            assert table.row_count == 2
            overview.query_one("#class-filter", Input).value = "bob"
            await pilot.pause()
            assert table.row_count == 1
            await pilot.press("e")
            assert isinstance(app.screen, TextInputDialog)
            output: Path = tmp_path / "turma.csv"
            app.screen.query_one("#value", Input).value = str(output)
            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, ReviewOverviewScreen)
            with output.open(encoding="utf-8", newline="") as stream:
                exported: list[dict[str, str]] = list(csv.DictReader(stream))
            assert [row["student"] for row in exported] == ["alice", "bob"]
            table.focus()
            await pilot.press("enter")
        assert app.return_value == ReviewTarget(1)
        assert context.selected_key == task.basic.full_key

    asyncio.run(exercise())
