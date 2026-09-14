import asyncio
from pathlib import Path

from tko.config.settings import Settings
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.ui_textual.app import TkoApp


def test_graph_axis_controls(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)
    task: Task = Task()

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None)
        async with app.run_test(size=(120, 35)) as pilot:
            await pilot.press("3", "4")
            assert repo.flags.panel.is_graph()
            assert repo.flags.task_graph_mode.is_executions()
            assert app._graph_lines(task, 60, 20) == []
            await pilot.press("4")
            assert repo.flags.task_graph_mode.is_time_view()
            assert app._graph_lines(task, 60, 20) == []
            await pilot.click("#top-graph")
            assert repo.flags.task_graph_mode.is_executions()
            await pilot.press("pagedown")
            assert repo.flags.task_graph_mode.is_time_view()
            await pilot.press("3", "4")
            assert repo.flags.task_graph_mode.is_time_view()
            await pilot.press("pageup")
            assert repo.flags.task_graph_mode.is_executions()

    asyncio.run(exercise())


def test_graph_footer_buttons_and_layout(tmp_path: Path) -> None:
    from textual.containers import Grid, ScrollableContainer, Vertical
    from textual.widgets import Button

    from tko.game.quest import Quest
    from tko.game.tree_item import IsTreeItem

    settings: Settings = Settings(tmp_path)
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)

    class GraphApp(TkoApp):
        selected: IsTreeItem | None = Task()

        def _selected_item(self) -> IsTreeItem | None:
            return self.selected

    async def exercise() -> None:
        app: GraphApp = GraphApp(settings, repo, None)
        async with app.run_test(size=(120, 35)) as pilot:
            footer: Grid = app.query_one("#graph-footer", Grid)
            time: Button = app.query_one("#graph-time", Button)
            executions: Button = app.query_one("#graph-executions", Button)
            await pilot.press("3")
            assert not footer.display
            await pilot.press("4")
            assert footer.display
            assert executions.has_class("active")
            assert not time.disabled
            assert str(time.label) == "Gráfico Tempo [PgDown]"
            assert str(executions.label) == "Gráfico Execução [PgUp]"
            for width in (80, 120):
                await pilot.resize_terminal(width, 35)
                await pilot.pause()
                frame: Vertical = app.query_one("#info-frame", Vertical)
                panel: ScrollableContainer = app.query_one("#side-panel", ScrollableContainer)
                assert footer.region in frame.region
                assert panel.region.bottom == footer.region.y
                assert footer.region.bottom == frame.content_region.bottom
                assert abs(time.size.width - executions.size.width) <= 1
                for button in (time, executions):
                    assert button.region in footer.region
                    if width == 120:
                        assert button.size.width >= len(str(button.label))
                await pilot.click("#graph-time")
                assert repo.flags.task_graph_mode.is_time_view()
                assert time.has_class("active")
                assert not executions.has_class("active")
                await pilot.click("#graph-executions")
                assert repo.flags.task_graph_mode.is_executions()
                assert executions.has_class("active")
            await pilot.press("pagedown")
            assert time.has_class("active")
            await pilot.press("pageup")
            assert executions.has_class("active")
            await pilot.press("4")
            assert time.has_class("active")
            for key in ("3", "5", "6"):
                await pilot.press(key)
                assert not footer.display
                await pilot.press("4")
                assert footer.display
                assert time.has_class("active")
            app.selected = Quest("Quest", "quest")
            app.refresh_panel()
            assert time.disabled and executions.disabled
            assert footer.display
            app.selected = None
            app.refresh_panel()
            assert time.disabled and executions.disabled

    asyncio.run(exercise())
