import asyncio
from tko.ui_textual.palette import ACCENT, BORDER
from pathlib import Path

from textual.color import Color
from textual.containers import ItemGrid, ScrollableContainer, Vertical
from textual.widgets import Button, Input

from tko.config.settings import Settings
from tko.game.quest import Quest
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.ui_textual.app import TkoApp, TaskTreeView


def test_tab_only_switches_play_panels(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None)
        async with app.run_test() as pilot:
            tree: TaskTreeView = app.query_one(TaskTreeView)
            panel: ScrollableContainer = app.query_one("#side-panel", ScrollableContainer)
            assert app.focused is tree
            for key in ("tab", "shift+tab"):
                await pilot.press(key)
                assert app.focused is panel
                await pilot.press(key)
                assert app.focused is tree
            app.query_one("#top-preview", Button).focus()
            await pilot.press("tab")
            assert app.focused is tree
            await pilot.press("slash")
            assert isinstance(app.focused, Input)
            await pilot.press("tab")
            assert app.focused is tree
            await pilot.press("tab")
            assert app.focused is panel

    asyncio.run(exercise())


def test_panel_headers_layout_clicks_and_focus(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)
    quest: Quest = Quest("Quest", "quest")
    task: Task = Task()
    task.basic.key = "task"
    task.quest_key = quest.basic.full_key
    quest.add_task(task)
    repo.game.quests = {quest.basic.full_key: quest}
    repo.game.ordered_quests = [quest.basic.full_key]
    repo.game.tasks = {task.basic.full_key: task}
    repo.data.pinned = [task.basic.full_key]

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None)
        async with app.run_test(size=(120, 35)) as pilot:
            left: Vertical = app.query_one("#task-frame", Vertical)
            right: Vertical = app.query_one("#info-frame", Vertical)
            tree: TaskTreeView = app.query_one(TaskTreeView)
            panel: ScrollableContainer = app.query_one("#side-panel", ScrollableContainer)
            left_header: ItemGrid = app.query_one("#task-header", ItemGrid)
            right_header: ItemGrid = app.query_one("#info-header", ItemGrid)
            assert [button.id for button in left_header.query(Button)] == ["top-all", "top-pinned"]
            assert [button.id for button in right_header.query(Button)] == [
                "top-preview", "top-graph", "top-logs", "top-skills",
            ]
            assert left.styles.border_top[1] == Color.parse(ACCENT)
            assert right.styles.border_top[1] == Color.parse(BORDER)
            for width in (80, 120):
                await pilot.resize_terminal(width, 35)
                await pilot.pause()
                for header in (left_header, right_header):
                    for button in header.query(Button):
                        assert button.region in header.region
                        assert button.size.width >= len(str(button.label)) + 2
                assert left_header.region.bottom <= tree.region.y
                assert right_header.region.bottom <= panel.region.y
                for identifier, mode in (
                    ("top-preview", "preview"), ("top-graph", "graph"),
                    ("top-logs", "logs"), ("top-skills", "skills"),
                ):
                    await pilot.click(f"#{identifier}")
                    assert repo.flags.panel.get_value() == mode
                    assert right.styles.border_top[1] == Color.parse(ACCENT)
                    assert left.styles.border_top[1] == Color.parse(BORDER)
                await pilot.press("tab")
                assert app.focused is tree
                await pilot.click("#top-all")
                assert repo.flags.task_view_mode.is_all()
                await pilot.click("#top-pinned")
                assert repo.flags.task_view_mode.is_pinned()
                await pilot.press("1")
                assert repo.flags.task_view_mode.is_all()
                await pilot.press("2")
                assert repo.flags.task_view_mode.is_pinned()
                await pilot.press("tab")
                assert app.focused is panel
                assert right.styles.border_top[1] == Color.parse(ACCENT)

    asyncio.run(exercise())
