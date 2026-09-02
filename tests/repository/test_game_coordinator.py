from pathlib import Path
from types import SimpleNamespace

from tko.config.run_settings import RunSettings
from tko.repository.git_cache import GitCache
from tko.repository.game_coordinator import GameCoordinator
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader


def test_ensure_managed_readmes_removes_missing_task_during_load(tmp_path: Path) -> None:
    index_file = tmp_path / "README.md"
    source_dir = tmp_path / "labs"
    source_dir.mkdir()
    index_file.write_text(
        "# labs\n\n"
        "- [ ] `@missing` [Missing](labs/missing/README.md)\n",
        encoding="utf-8",
    )
    remote = SimpleNamespace(name="labs")
    repo = SimpleNamespace(sources={"labs": remote})
    resolver = SimpleNamespace(
        is_local_internal=lambda _remote: True,  # type: ignore[attr-defined]
        source_work_dir=lambda _source: source_dir,  # type: ignore[attr-defined]
        resolve_index_file=lambda _remote, load_git=False: (index_file, True),  # type: ignore[attr-defined]
    )

    GameCoordinator(repo).ensure_managed_readmes_fixed(  # type: ignore[arg-type]
        repo,  # type: ignore[arg-type]
        resolver,  # type: ignore[arg-type]
    )

    assert "labs/missing/README.md" not in index_file.read_text(encoding="utf-8")


def test_load_game_exposes_the_same_unique_tasks_in_quests_and_task_map(tmp_path: Path) -> None:
    index_file = tmp_path / "README.md"
    index_file.write_text(
        "# Course\n\n"
        "## First <!-- @first -->\n"
        "- [ ] `@same type=read` [First](first/README.md)\n"
        "## Second <!-- @second -->\n"
        "- [ ] `@same type=read` [Duplicate](first/README.md)\n"
        "- [ ] `@unique type=read` [Unique](unique/README.md)\n",
        encoding="utf-8",
    )
    (tmp_path / "first").mkdir()
    (tmp_path / "first" / "README.md").write_text("# First\n", encoding="utf-8")
    (tmp_path / "unique").mkdir()
    (tmp_path / "unique" / "README.md").write_text("# Unique\n", encoding="utf-8")
    rs = RunSettings(changedir=tmp_path)
    rs.force_offline = True
    repo = Repository(
        tmp_path,
        rs=rs,
        git_cache=GitCache(tmp_path / "git-cache", update_mode=rs.update_mode),
        recursive_search=False,
    )
    RepositoryLoader(repo).save(force=True)

    RepositoryLoader(repo).load()
    GameCoordinator(repo).load_game()

    quest_task_keys = [
        task.basic.full_key
        for quest in repo.game.quests.values()
        for task in quest.get_tasks()
    ]
    assert quest_task_keys == ["labs@same", "labs@unique"]
    assert list(repo.game.tasks) == quest_task_keys
