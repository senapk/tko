import asyncio
from pathlib import Path

from textual.containers import ScrollableContainer
from textual.widgets import Button, Input

from tko.config.settings import Settings
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
