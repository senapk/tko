from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from tko.config.run_settings import RunSettings
from tko.repository.linked_profile import LinkedProfileService
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader, dumps_repository_toml
from tko.repository.repository_data import ConfigDict


def make_repo(tmp_path: Path) -> Repository:
    return Repository(tmp_path, RunSettings(changedir=tmp_path), git_cache=None, recursive_search=False)


def valid_profile() -> str:
    return """
version = "0.1"
name = "POO 2026.2"
authoring_source = "labs"
language = "java"

[audit]
enabled = true
interval_seconds = 20

[sources.labs]
uri = "README.md"

[sources.poo]
uri = "https://github.com/professor/poo/blob/main/README.md"
"""


def test_parse_remote_profile_becomes_repository_profile(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    loaded = LinkedProfileService(repo).parse_and_validate(valid_profile())

    assert loaded["name"] == "POO 2026.2"
    assert loaded["authoring_source"] == "labs"
    assert loaded["language"] == "java"
    assert cast(ConfigDict, loaded["audit"])["enabled"] is True
    assert "poo" in cast(ConfigDict, loaded["sources"])


def test_parse_remote_profile_accepts_kotlin_language(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    loaded = LinkedProfileService(repo).parse_and_validate(valid_profile().replace("java", "kt"))

    assert loaded["language"] == "kt"


def test_rejects_unknown_fields(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    with pytest.raises(ValueError, match="campo desconhecido|unknown field"):
        LinkedProfileService(repo).parse_and_validate(valid_profile() + "\nunknown = true\n")


def test_rejects_authoring_source_outside_workspace(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    content = """
version = "0.1"
authoring_source = "labs"

[sources.labs]
uri = "../README.md"
"""

    with pytest.raises(ValueError, match="fora do workspace|outside"):
        LinkedProfileService(repo).parse_and_validate(content)


def test_load_local_profile_records_link_metadata(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    profile_path = tmp_path / "profile.toml"
    profile_path.write_text(valid_profile(), encoding="utf-8")

    loaded = LinkedProfileService(repo).load("profile.toml")
    LinkedProfileService(repo).apply_loaded(loaded)

    assert repo.data.is_linked is True
    assert repo.data.link is not None
    assert repo.data.link.uri == profile_path.as_posix()
    assert repo.data.link.content_hash.startswith("sha256:")
    assert repo.data.profile_language == "java"


def test_dumps_repository_toml_writes_link_before_profile(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    profile_path = tmp_path / "profile.toml"
    profile_path.write_text(valid_profile(), encoding="utf-8")
    loaded = LinkedProfileService(repo).load("profile.toml")
    LinkedProfileService(repo).apply_loaded(loaded)

    text = dumps_repository_toml(repo.data.to_dict())

    assert "[link]" in text
    assert 'uri = "' + profile_path.as_posix() + '"' in text
    assert "[profile]" in text
    assert 'language = "java"' in text


def test_loader_refreshes_due_link_atomically(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    profile_path = tmp_path / "profile.toml"
    profile_path.write_text(valid_profile(), encoding="utf-8")
    loaded = LinkedProfileService(repo).load("profile.toml")
    LinkedProfileService(repo).apply_loaded(loaded)
    assert repo.data.link is not None
    repo.data.link.updated_at = "2000-01-01T00:00:00Z"
    RepositoryLoader(repo).save(force=True)

    profile_path.write_text(valid_profile().replace("java", "py"), encoding="utf-8")
    RepositoryLoader(repo).load()

    assert repo.data.profile_language == "py"
