import asyncio
from types import SimpleNamespace

from textual.app import App, ComposeResult

from tko.game.quest import Quest
from tko.game.task import Task
from tko.ui_textual.app import TaskTreeView
from tko.util.rt import RT


class _TreeModel:
    def __init__(self, quest: Quest, task: Task) -> None:
        self.quest = quest
        self.task = task
        self.state = SimpleNamespace(selected=task.basic.full_key, expanded={quest.basic.full_key})

    def update(self) -> None:
        pass

    def get_rendered_items(self) -> list[tuple[RT, Quest | Task]]:
        return [(RT("Quest", "y"), self.quest), (RT("Task", "g"), self.task)]


def test_tree_view_rebuilds_hierarchy_and_restores_selection() -> None:
    quest = Quest("Quest", "quest")
    quest.basic.source_name = "source"
    task = Task()
    task.basic.source_name = "source"
    task.basic.key = "task"
    task.quest_key = quest.basic.full_key
    model = _TreeModel(quest, task)

    class TreeApp(App[None]):
        def compose(self) -> ComposeResult:
            yield TaskTreeView(model)

        def on_mount(self) -> None:
            self.query_one(TaskTreeView).rebuild()

    async def exercise() -> None:
        app = TreeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            view = app.query_one(TaskTreeView)
            assert len(view.root.children) == 1
            assert len(view.root.children[0].children) == 1
            assert view.cursor_node is not None
            assert view.cursor_node.data is task

    asyncio.run(exercise())
