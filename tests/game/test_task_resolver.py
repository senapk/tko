from pathlib import Path
from dataclasses import replace

from tko.game.task import Task
from tko.game.task_enums import EvalMode
from tko.game.task_resolver import TaskResolver
from tko.repository.git_cache import GitCache


def make_external_task(key: str) -> Task:
    task = Task()
    task.basic.source_name = "disc"
    task.basic.key = key
    task.location = replace(task.location, eval=EvalMode.DIFF, external_source=True)
    return task


def test_task_resolver_uses_canonical_path_for_new_key(tmp_path: Path) -> None:
    canonical = tmp_path / "disc" / "labs" / "carro"
    canonical.mkdir(parents=True)

    resolver = TaskResolver(GitCache(tmp_path / "cache"), tmp_path)

    assert resolver.target_folder(make_external_task("labs/carro")) == canonical


def test_task_resolver_does_not_fall_back_to_old_path(tmp_path: Path) -> None:
    legacy = tmp_path / "disc" / "carro"
    legacy.mkdir(parents=True)

    resolver = TaskResolver(GitCache(tmp_path / "cache"), tmp_path)

    assert resolver.target_folder(make_external_task("labs/carro")) == tmp_path / "disc/labs/carro"


def test_task_resolver_does_not_add_labs_to_bare_key(tmp_path: Path) -> None:
    canonical = tmp_path / "disc" / "labs" / "carro"
    canonical.mkdir(parents=True)

    resolver = TaskResolver(GitCache(tmp_path / "cache"), tmp_path)

    assert resolver.target_folder(make_external_task("carro")) == tmp_path / "disc/carro"
