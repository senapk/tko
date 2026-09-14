from pathlib import Path

import pytest

from tko.cmds.cmd_down import CmdDown
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.repository.git_cache import GitCache, UpdateMode
from tko.repository.remote import Source
from tko.repository.repository import Repository


@pytest.mark.parametrize("index_path", ["README.md", "course/README.md"])
def test_remote_snapshot_download_uses_cached_activity(tmp_path: Path, index_path: str) -> None:
    cache: GitCache = GitCache(tmp_path / "cache", update_mode=UpdateMode.NEVER)
    source: Source = Source.from_uri(
        "poo", f"https://github.com/example/course/blob/main/{index_path}"
    )
    cached_repo: Path = cache._repo_dir("https://github.com/example/course")
    cached_index: Path = cached_repo / index_path
    origin: Path = cached_index.parent / "labs" / "relogio"
    origin.mkdir(parents=True)
    cached_index.write_text(
        "# Course\n\n- [ ] `eval=none` [Clock](labs/relogio/README.md)\n",
        encoding="utf-8",
    )
    description: str = "# Clock\n\nKeep the time.\n"
    (origin / "README.md").write_text(description, encoding="utf-8")
    repo: Repository = Repository(tmp_path / "workspace", RunSettings(), cache)
    repo.data.lang = "py"
    repo.game.set_sources({"poo": source}, "py")
    repo.game.build(repo.source_resolver)
    task = repo.game.get_task_throw("poo@labs/relogio")

    assert task.location.index_path == repo.root_dir / "poo" / index_path
    assert task.location.raw_link == "labs/relogio/README.md"
    assert repo.task_resolver.origin_file(task, load_git=False) == origin / "README.md"
    assert CmdDown(repo, task.basic.full_key, Settings(tmp_path / "settings")).execute()
    destination: Path = repo.root_dir / "poo" / "labs" / "relogio" / "README.md"
    assert destination.read_text(encoding="utf-8") == description

    destination.write_text("", encoding="utf-8")
    assert CmdDown(repo, task.basic.full_key, Settings(tmp_path / "settings")).execute()
    assert destination.read_text(encoding="utf-8") == description
    assert (origin / "README.md").read_text(encoding="utf-8") == description
