from dataclasses import FrozenInstanceError

import pytest

from tko.util.git_hub_url import GitHubUrl


def test_empty_structure_starts_with_blank_fields() -> None:
    structure = GitHubUrl()

    assert structure.user == ""
    assert structure.repo == ""
    assert structure.branch == ""
    assert structure.relative_path == ""


def test_structure_builds_repository_github_and_raw_urls() -> None:
    structure = GitHubUrl(
        user="user",
        repo="repo",
        branch="main",
        relative_path="folder/file.md",
        path_type="blob",
    )

    assert structure.repository_url == "https://github.com/user/repo"
    assert structure.blob_url == "https://github.com/user/repo/blob/main/folder/file.md"
    assert (
        structure.raw_file_url
        == "https://raw.githubusercontent.com/user/repo/main/folder/file.md"
    )


def test_structure_is_immutable() -> None:
    structure = GitHubUrl(user="user", repo="repo")

    with pytest.raises(FrozenInstanceError):
        structure.user = "other"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("url", "relative_path", "path_type", "github_url"),
    [
        (
            "https://github.com/user/repo/blob/main/folder/file.md",
            "folder/file.md",
            "blob",
            "https://github.com/user/repo/blob/main/folder/file.md",
        ),
        (
            "https://github.com/user/repo/tree/main/folder/sub",
            "folder/sub",
            "tree",
            "https://github.com/user/repo/tree/main/folder/sub",
        ),
        (
            "https://github.com/user/repo/blob/main",
            "",
            "blob",
            "https://github.com/user/repo/tree/main",
        ),
        (
            "https://github.com/user/repo/tree/main/",
            "",
            "tree",
            "https://github.com/user/repo/tree/main",
        ),
    ],
)
def test_parse_accepts_github_blob_and_tree_urls(
    url: str, relative_path: str, path_type: str, github_url: str
) -> None:
    structure = GitHubUrl.parse(url)

    assert structure is not None
    assert structure.user == "user"
    assert structure.repo == "repo"
    assert structure.branch == "main"
    assert structure.relative_path == relative_path
    assert structure.path_type == path_type
    assert structure.blob_url == github_url


def test_parse_accepts_github_repository_without_branch_or_path() -> None:
    structure = GitHubUrl.parse("https://github.com/user/repo")

    assert structure is not None
    assert structure.user == "user"
    assert structure.repo == "repo"
    assert structure.branch == ""
    assert structure.relative_path == ""
    assert structure.repository_url == "https://github.com/user/repo"
    assert structure.branch_tree_url == "https://github.com/user/repo"
    assert structure.blob_url == "https://github.com/user/repo"
    assert structure.raw_file_url == ""


def test_structure_with_path_without_branch_stays_at_repository_url() -> None:
    structure = GitHubUrl(
        user="user",
        repo="repo",
        relative_path="folder/file.md",
        path_type="blob",
    )

    assert structure.blob_url == "https://github.com/user/repo"
    assert structure.raw_file_url == ""


def test_parse_accepts_raw_url_with_branch_and_without_relative_path() -> None:
    structure = GitHubUrl.parse("https://raw.githubusercontent.com/user/repo/main")

    assert structure is not None
    assert structure.branch == "main"
    assert structure.relative_path == ""
    assert structure.blob_url == "https://github.com/user/repo/tree/main"
    assert structure.raw_file_url == "https://raw.githubusercontent.com/user/repo/main"


def test_parse_accepts_raw_githubusercontent_refs_heads_url() -> None:
    structure = GitHubUrl.parse(
        "https://raw.githubusercontent.com/user/repo/refs/heads/main/folder/file.md"
    )

    assert structure is not None
    assert structure.user == "user"
    assert structure.repo == "repo"
    assert structure.branch == "main"
    assert structure.relative_path == "folder/file.md"
    assert structure.path_type == "blob"


def test_parse_accepts_raw_githubusercontent_url_without_refs_heads() -> None:
    structure = GitHubUrl.parse(
        "https://raw.githubusercontent.com/user/repo/main/folder/file.md"
    )

    assert structure is not None
    assert structure.branch == "main"
    assert structure.relative_path == "folder/file.md"
    assert structure.blob_url == "https://github.com/user/repo/blob/main/folder/file.md"


def test_parse_ignores_query_and_fragment() -> None:
    structure = GitHubUrl.parse(
        "https://github.com/user/repo/blob/main/folder/file.md?raw=1#L10"
    )

    assert structure is not None
    assert structure.relative_path == "folder/file.md"


def test_with_relative_path_returns_new_structure() -> None:
    structure = GitHubUrl(user="user", repo="repo", branch="main")

    updated = structure.with_relative_path("docs/readme.md", "blob")

    assert structure.relative_path == ""
    assert updated.relative_path == "docs/readme.md"
    assert updated.path_type == "blob"
    assert updated.raw_base_url == "https://raw.githubusercontent.com/user/repo/main/docs"
    assert updated.github_blob_base_url == "https://github.com/user/repo/blob/main/docs"
    assert updated.github_tree_base_url == "https://github.com/user/repo/tree/main/docs"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/user/repo/blob/main/file.md",
        "https://github.com/user/repo/commit/main/file.md",
        "not a url",
    ],
)
def test_parse_rejects_unsupported_urls(url: str) -> None:
    assert GitHubUrl.parse(url) is None
