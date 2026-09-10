from pathlib import Path
from types import SimpleNamespace

from tko.config.run_settings import RunSettings
from tko.repository.git_cache import GitCache, UpdateMode
from tko.repository.game_coordinator import GameCoordinator
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader
from tko.repository.remote import Source
from tko.game.game import Game
from tko.repository.remote_resolver import SourceResolver


def test_ensure_managed_readmes_removes_missing_task_during_load(tmp_path: Path) -> None:
    index_file = tmp_path / "README.md"
    source_dir = tmp_path / "labs"
    source_dir.mkdir()
    index_file.write_text(
        "# labs\n\n"
            "- [ ] `@missing eval=none` [Missing](labs/missing/README.md)\n",
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


def test_managed_source_normalizes_task_key_to_path(tmp_path: Path) -> None:
    index_file = tmp_path / "README.md"
    source_dir = tmp_path / "labs"
    task_dir = source_dir / "task"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Task\n", encoding="utf-8")
    index_file.write_text(
        "- [ ] `@wrong eval=none` [Task](labs/task/README.md)\n", encoding="utf-8"
    )
    remote = SimpleNamespace(name="labs")
    repo = SimpleNamespace(sources={"labs": remote})
    resolver = SimpleNamespace(
        is_local_internal=lambda _remote: True,
        source_work_dir=lambda _source: source_dir,
        resolve_index_file=lambda _remote, load_git=False: (index_file, True),
    )
    GameCoordinator(repo).ensure_managed_readmes_fixed(repo, resolver)

    content = index_file.read_text(encoding="utf-8")
    assert "[Task](labs/task/README.md)" in content
    assert "@wrong" not in content


def test_load_game_exposes_the_same_unique_tasks_in_quests_and_task_map(tmp_path: Path) -> None:
    index_file = tmp_path / "README.md"
    index_file.write_text(
        "# Course\n\n"
        "## First <!-- @first -->\n"
        "- [ ] `eval=none` [First](same/README.md)\n"
        "## Second <!-- @second -->\n"
        "- [ ] `eval=none` [Duplicate](same/README.md)\n"
        "- [ ] `eval=none` [Unique](unique/README.md)\n",
        encoding="utf-8",
    )
    (tmp_path / "same").mkdir()
    (tmp_path / "same" / "README.md").write_text("# First\n", encoding="utf-8")
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


def test_game_loads_remote_source_from_materialized_index_offline(tmp_path: Path) -> None:
    snapshot = tmp_path / "disc" / "README.md"
    snapshot.parent.mkdir()
    snapshot.write_text(
        "# Course\n\n"
        "## Basics key=@basics\n"
            "- [ ] `eval=none` [Carro](labs/carro/README.md)\n",
        encoding="utf-8",
    )
    source = Source.from_git_file("disc", "https://github.com/user/course", index="README.md")
    assert source is not None
    resolver = SourceResolver(
        GitCache(tmp_path / "missing-cache", update_mode=UpdateMode.NEVER),
        tmp_path,
    )
    game = Game().set_sources({"disc": source}, language="")

    game.build(resolver)

    assert "disc@labs/carro" in game.tasks
