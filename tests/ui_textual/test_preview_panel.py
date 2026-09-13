import asyncio
from pathlib import Path

from rich.markdown import Markdown
from textual.containers import ScrollableContainer
from textual.widgets import Button, Static

from tko.config.settings import Settings
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.task_location import TaskLocation
from tko.repository.repository import Repository
from tko.ui_textual.app import TkoApp, TaskTreeView


def test_preview_selection_rendering_and_scroll(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    settings.app.ui_language = "en"
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)
    quest: Quest = Quest("Quest", "quest")
    quest.basic.source_name = "course"
    tasks: list[Task] = []
    for index in range(2):
        readme: Path = tmp_path / f"task{index}.md"
        readme.write_text(f"# Task {index}\n\n" + "Paragraph with **bold**.\n\n" * 80, encoding="utf-8")
        task: Task = Task()
        task.basic.source_name = "course"
        task.basic.key = f"task{index}"
        task.basic.title = f"Task {index}"
        task.quest_key = quest.basic.full_key
        task.location = TaskLocation(index_path=tmp_path / "README.md", raw_link=readme.name)
        quest.add_task(task)
        tasks.append(task)
    repo.game.quests = {quest.basic.full_key: quest}
    repo.game.ordered_quests = [quest.basic.full_key]
    repo.game.tasks = {task.basic.full_key: task for task in tasks}
    repo.data.expanded = [quest.basic.full_key]
    repo.data.selected = quest.basic.full_key
    repo.flags.task_view_mode.set_view_all()

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None)
        async with app.run_test(size=(120, 35)) as pilot:
            await pilot.pause()
            await pilot.press("3")
            content: Static = app.query_one("#side-content", Static)
            panel: ScrollableContainer = app.query_one("#side-panel", ScrollableContainer)
            assert repo.flags.panel.is_preview()
            assert app.query_one("#top-preview", Button).has_class("active")
            assert "Select a task" in str(content.content)
            await pilot.press("down")
            await pilot.pause()
            assert isinstance(content.content, Markdown)
            assert content.content.markup.startswith("# Task 0")
            await pilot.press("pagedown")
            await pilot.pause()
            assert panel.scroll_y > 0
            previous: float = panel.scroll_y
            await pilot.resize_terminal(110, 35)
            await pilot.pause()
            assert panel.scroll_y == previous
            await pilot.press("pageup")
            await pilot.pause()
            assert panel.scroll_y < previous
            await pilot.press("down")
            await pilot.pause()
            assert isinstance(content.content, Markdown)
            assert content.content.markup.startswith("# Task 1")
            assert panel.scroll_y == 0
            await pilot.press("up", "up")
            assert "Select a task" in str(content.content)
            for key in ("4", "5", "6"):
                await pilot.press(key)
                assert not isinstance(content.content, Markdown)
                assert not content.has_class("preview")
            await pilot.click("#top-preview")
            assert repo.flags.panel.is_preview()
            app.query_one(TaskTreeView).focus()
            await pilot.press("down")
            await pilot.pause()
            (tmp_path / "task0.md").unlink()
            app.refresh_panel()
            assert "unavailable" in str(content.content)

    asyncio.run(exercise())
