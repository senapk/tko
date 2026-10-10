"""The first screen should settle without rebuilding the tree repeatedly."""

from __future__ import annotations

import asyncio
from pathlib import Path

from pytest import MonkeyPatch

from tko.config.settings import Settings
from tko.repository.repository import Repository
from tko.ui_textual.app import TaskTreeView, TkoApp


def test_initial_screen_rebuilds_tree_at_most_three_times(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    settings: Settings = Settings(tmp_path / "settings")
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)
    rebuild = TaskTreeView.rebuild
    calls: list[int] = []

    def counted_rebuild(tree: TaskTreeView) -> None:
        calls.append(1)
        rebuild(tree)

    monkeypatch.setattr(TaskTreeView, "rebuild", counted_rebuild)

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.query_one(TaskTreeView).is_mounted

    asyncio.run(exercise())

    assert 1 <= len(calls) <= 3
