from pathlib import Path

from tko.config.settings import Settings
from tko.config.flags import Flags
from tko.game.quest import Quest
from tko.game.task import Task
from tko.logger.log_item_exec import LogItemExec
from tko.play_gui.gui_graph_panel import GuiGraphPanel
from tko.repository.repository import Repository


def _panel(tmp_path: Path, keys: list[str]) -> tuple[GuiGraphPanel, Quest]:
    settings: Settings = Settings(tmp_path)
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)
    quest: Quest = Quest("Selected", "selected")
    quest.basic.source_name = "src"
    task: Task = Task()
    task.basic.source_name = "src"
    task.basic.key = "plan/one"
    task.quest_key = "src@selected"
    quest.add_task(task)
    repo.game.tasks[task.basic.full_key] = task
    for index, key in enumerate(keys):
        for minute in (0, 2):
            event: LogItemExec = LogItemExec()
            event.key = key
            event.set_timestamp(f"2026-09-14 {index + 10:02d}:{minute:02d}:00")
            repo.logger.tasks.handle_log_entry(event)
    return GuiGraphPanel(settings, repo, Flags()), quest


def test_history_filters_full_identity_before_display_strips_source(tmp_path: Path) -> None:
    panel, quest = _panel(tmp_path, ["src@plan/other", "other@plan/one", "src@plan/one"])
    made, header, rows = panel.get_history(quest)
    assert made
    assert len(header) == 1
    assert len(rows) == 1
    assert "plan/one" in str(rows[0])
    assert len(panel.get_history()[2]) == 3


def test_history_does_not_invent_legacy_equivalences(tmp_path: Path) -> None:
    panel, quest = _panel(tmp_path, ["src@one", "src@labs/one"])
    assert panel.get_history(quest)[2] == []
