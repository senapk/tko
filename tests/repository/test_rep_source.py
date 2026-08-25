from pathlib import Path

import pytest

from tko.repository.remote import DEFAULT_INDEX, Remote, SourceType
from tko.repository.sandbox import REMOTE_NAME, Sandbox


def test_sandbox_name_matches_reserved_remote_name() -> None:
    assert Sandbox.get_sandbox_name() == REMOTE_NAME


def test_is_sandbox_checks_remote_name() -> None:
    assert Sandbox.is_sandbox(Remote(name=REMOTE_NAME)) is True
    assert Sandbox.is_sandbox(Remote(name="disc")) is False

def test_from_local_file_keeps_absolute_file_path(tmp_path: Path) -> None:
    source_dir = tmp_path / "materials"
    index_file = source_dir / DEFAULT_INDEX

    remote = Remote.from_local_file("disc", index_file, is_editable=False)

    assert remote.path_or_url == index_file.as_posix()
    assert remote.is_editable is False


def test_from_local_file_uses_default_index_for_directory(tmp_path: Path) -> None:
    source_dir = tmp_path / "materials"
    source_dir.mkdir()

    remote = Remote.from_local_file("disc", source_dir, is_editable=True)

    assert remote.path_or_url == (source_dir / DEFAULT_INDEX).as_posix()
    assert remote.is_editable is True


def test_from_git_file_builds_blob_url_with_branch_and_index() -> None:
    remote = Remote.from_git_file(
        "disc",
        "https://github.com/user/repo",
        branch="develop",
        index="INDEX.md",
    )

    assert remote is not None
    assert remote.name == "disc"
    assert remote.path_or_url == "https://github.com/user/repo/blob/develop/INDEX.md"
    assert remote.source_type == SourceType.GIT_SOURCE
    assert remote.is_editable is False


def test_from_git_file_returns_none_for_invalid_url() -> None:
    assert Remote.from_git_file("disc", "https://example.com/repo.git") is None


def test_load_from_dict_supports_legacy_git_fields() -> None:
    remote = Remote.from_dict(
        {
            "alias": "legacy",
            "target": "https://github.com/user/repo",
            "branch": "dev",
            "type": "git",
            "writeable": False,
            "index": "custom.md",
        }
    )

    assert remote.name == "legacy"
    assert remote.source_type == SourceType.GIT_SOURCE
    assert remote.is_editable is False
    assert remote.path_or_url == "https://github.com/user/repo/blob/dev/custom.md"


def test_load_from_dict_uses_path_or_url_when_present() -> None:
    remote = Remote.from_dict(
        {
            "name": "disc",
            "path_or_url": "materials/README.md",
            "type": "local",
            "writeable": True,
        }
    )

    assert remote == Remote.from_local_file("disc", Path("materials/README.md"), is_editable=True)


def test_save_to_dict_persists_expected_fields() -> None:
    remote = Remote.from_git_file("disc", "https://github.com/user/repo", branch="develop", index="INDEX.md")
    assert remote is not None

    saved = remote.to_dict()

    assert saved == {
        "name": "disc",
        "type": "git",
        "writeable": False,
        "path_or_url": "https://github.com/user/repo/blob/develop/INDEX.md",
    }


def test_from_dict_raises_value_error_for_invalid_git_source() -> None:
    with pytest.raises(ValueError, match="Invalid git source"):
        Remote.from_dict({"name": "disc", "target": "https://example.com/repo.git", "type": "git"})
