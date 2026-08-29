from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from tko.repository.game_coordinator import GameCoordinator


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
    repo = SimpleNamespace(remotes={"labs": remote})
    resolver = SimpleNamespace(
        is_local_internal=lambda _remote: True,
        remote_work_dir=lambda _remote: source_dir,
        resolve_index_file=lambda _remote, load_git=False: (index_file, True),
    )

    GameCoordinator(cast(Any, repo)).ensure_managed_readmes_fixed(
        cast(Any, repo),
        cast(Any, resolver),
    )

    assert "labs/missing/README.md" not in index_file.read_text(encoding="utf-8")
