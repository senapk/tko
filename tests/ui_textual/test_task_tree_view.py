import asyncio

from rich.style import Style
from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Tree

from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.ui_textual.app import TaskTreeView
from tko.util.rt import RT


class _TreeState:
    def __init__(self, selected: str, expanded: set[str]) -> None:
        self.selected: str = selected
        self.expanded: set[str] = expanded


class _TaskFormatter:
    def __init__(self, materialized: bool = True) -> None:
        self.materialized = materialized

    def is_downloaded_for_lang(self, task: Task) -> bool:
        del task
        return self.materialized


class _TreeModel:
    def __init__(self, quest: Quest, task: Task, *, materialized: bool = True) -> None:
        self.quest = quest
        self.task = task
        self.state: _TreeState = _TreeState(task.basic.full_key, {quest.basic.full_key})
        self.task_formatter: _TaskFormatter = _TaskFormatter(materialized)

    def update(self) -> None:
        pass

    def get_rendered_items(self) -> list[tuple[RT, IsTreeItem]]:
        return [(RT("Quest", "y"), self.quest), (RT("Task", "g"), self.task)]

    def move_left(self) -> None:
        pass

    def move_right(self) -> None:
        pass


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
            await pilot.pause()
            view = app.query_one(TaskTreeView)
            assert len(view.root.children) == 1
            assert len(view.root.children[0].children) == 1
            assert view.cursor_node is not None
            assert view.cursor_node.data is task

    asyncio.run(exercise())


def test_mouse_click_selects_task_without_emitting_activation() -> None:
    quest = Quest("Quest", "quest")
    quest.basic.source_name = "source"
    task = Task()
    task.basic.source_name = "source"
    task.basic.key = "task"
    task.quest_key = quest.basic.full_key
    model = _TreeModel(quest, task)

    class TreeApp(App[None]):
        def __init__(self) -> None:
            super().__init__()
            self.activations: list[Task] = []

        def compose(self) -> ComposeResult:
            yield TaskTreeView(model)

        def on_mount(self) -> None:
            self.query_one(TaskTreeView).rebuild()

        def on_tree_node_selected(self, event: Tree.NodeSelected[Quest | Task]) -> None:
            if isinstance(event.node.data, Task):
                self.activations.append(event.node.data)

    async def exercise() -> None:
        app = TreeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            view = app.query_one(TaskTreeView)
            task_node = view.root.children[0].children[0]
            model.state.selected = quest.basic.full_key
            event = events.Click(
                view, 0, 0, 0, 0, 1, False, False, False,
                style=Style(meta={"node": task_node.id}),
            )
            await view._on_message(event)
            assert view.cursor_node is task_node
            assert model.state.selected == task.basic.full_key
            await pilot.pause()
            assert app.activations == []

    asyncio.run(exercise())


def test_mouse_click_selects_quest_without_changing_expansion() -> None:
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
            quest_node = view.root.children[0]
            event = events.Click(
                view, 0, 0, 0, 0, 1, False, False, False,
                style=Style(meta={"node": quest_node.id}),
            )
            await view._on_message(event)
            assert quest_node.is_expanded
            assert model.state.selected == quest.basic.full_key

    asyncio.run(exercise())


def test_double_click_on_quest_toggles_its_fold() -> None:
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
            quest_node = view.root.children[0]
            event = events.Click(
                view, 0, 0, 0, 0, 1, False, False, False,
                style=Style(meta={"node": quest_node.id}), chain=2,
            )
            await view._on_message(event)
            assert quest.basic.full_key not in model.state.expanded
            assert not view.root.children[0].is_expanded

    asyncio.run(exercise())


def test_double_click_on_materialized_task_emits_the_enter_activation_event() -> None:
    quest = Quest("Quest", "quest")
    quest.basic.source_name = "source"
    task = Task()
    task.basic.source_name = "source"
    task.basic.key = "task"
    task.quest_key = quest.basic.full_key
    model = _TreeModel(quest, task)

    class TreeApp(App[None]):
        def __init__(self) -> None:
            super().__init__()
            self.activations: list[Task] = []

        def compose(self) -> ComposeResult:
            yield TaskTreeView(model)

        def on_mount(self) -> None:
            self.query_one(TaskTreeView).rebuild()

        def on_tree_node_selected(self, event: Tree.NodeSelected[Quest | Task]) -> None:
            if isinstance(event.node.data, Task):
                self.activations.append(event.node.data)

    async def exercise() -> None:
        app = TreeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            view = app.query_one(TaskTreeView)
            task_node = view.root.children[0].children[0]
            event = events.Click(
                view, 0, 0, 0, 0, 1, False, False, False,
                style=Style(meta={"node": task_node.id}), chain=2,
            )
            await view._on_message(event)
            await pilot.pause()
            assert app.activations == [task]

    asyncio.run(exercise())


def test_double_click_on_unmaterialized_task_does_not_activate_it() -> None:
    quest = Quest("Quest", "quest")
    quest.basic.source_name = "source"
    task = Task()
    task.basic.source_name = "source"
    task.basic.key = "task"
    task.quest_key = quest.basic.full_key
    model = _TreeModel(quest, task, materialized=False)

    class TreeApp(App[None]):
        def __init__(self) -> None:
            super().__init__()
            self.activations: list[Task] = []

        def compose(self) -> ComposeResult:
            yield TaskTreeView(model)

        def on_mount(self) -> None:
            self.query_one(TaskTreeView).rebuild()

        def on_tree_node_selected(self, event: Tree.NodeSelected[Quest | Task]) -> None:
            if isinstance(event.node.data, Task):
                self.activations.append(event.node.data)

    async def exercise() -> None:
        app = TreeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            view = app.query_one(TaskTreeView)
            task_node = view.root.children[0].children[0]
            event = events.Click(
                view, 0, 0, 0, 0, 1, False, False, False,
                style=Style(meta={"node": task_node.id}), chain=2,
            )
            await view._on_message(event)
            await pilot.pause()
            assert app.activations == []

    asyncio.run(exercise())
