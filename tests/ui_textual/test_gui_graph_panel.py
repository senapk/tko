from pathlib import Path
from types import SimpleNamespace
from typing import cast

from tko.collect.task_collected import TaskCollected
from tko.config.settings import Settings
from tko.config.flags import Flags
from tko.game.quest import Quest
from tko.game.task import Task
from tko.play_gui.gui_graph_panel import GuiGraphPanel
from tko.repository.repository import Repository


def _task(source: str, key: str, quest_key: str) -> Task:
    task = Task()
    task.basic.source_name = source
    task.basic.key = key
    task.quest_key = f"{source}@{quest_key}"
    return task


def _history_item(key: str, quest: str) -> TaskCollected:
    item = TaskCollected()
    item.key = key
    item.quest = quest
    item.get_kv = lambda include_key, include_quest: {
        "remote": "",
        "duration": 2.0,
        "grader": " 10",
    }
    return item


def test_history_can_be_limited_to_selected_quest(tmp_path: Path) -> None:
    quest = Quest("Selected", "selected")
    quest.basic.source_name = "src"
    quest.add_task(_task("src", "labs/one", "selected"))
    other = _history_item("labs/other", "other")
    selected = _history_item("labs/one", "selected")
    logger = SimpleNamespace(tasks=SimpleNamespace(mount_task_history=lambda game, paths: [other, selected]))
    repo = SimpleNamespace(sources={}, logger=logger, game=SimpleNamespace())
    panel = GuiGraphPanel(Settings(tmp_path), cast(Repository, repo), cast(Flags, SimpleNamespace()))

    made, header, rows = panel.get_history(quest)

    assert made
    assert len(header) == 1
    assert len(rows) == 1
    assert "labs/one" in str(rows[0])


def test_history_accepts_legacy_task_key_for_selected_quest(tmp_path: Path) -> None:
    quest = Quest("Selected", "selected")
    quest.basic.source_name = "src"
    quest.add_task(_task("src", "one", "selected"))
    item = _history_item("labs/one", "selected")
    logger = SimpleNamespace(tasks=SimpleNamespace(mount_task_history=lambda game, paths: [item]))
    repo = SimpleNamespace(sources={}, logger=logger, game=SimpleNamespace())
    panel = GuiGraphPanel(Settings(tmp_path), cast(Repository, repo), cast(Flags, SimpleNamespace()))

    _, _, rows = panel.get_history(quest)

    assert len(rows) == 1
