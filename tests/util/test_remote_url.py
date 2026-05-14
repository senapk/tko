import pytest
from tko.util.github_url import GitHubUrl


def test_url_without_https_raises_value_error() -> None:
    with pytest.raises(ValueError):
        GitHubUrl("http://github.com/user/repo/blob/main/folder/file.md")


def test_url_without_scheme_raises_value_error() -> None:
    with pytest.raises(ValueError):
        GitHubUrl("github.com/user/repo/blob/main/folder/file.md")


def test_gist_url_sets_raw_link() -> None:
    url: str = "https://gist.githubusercontent.com/user/abc123/raw/abc/file.md"
    r: GitHubUrl = GitHubUrl(url)
    assert r.raw_link == url
    assert r.url_structure is None


def test_gist_url_get_raw_url() -> None:
    url: str = "https://gist.githubusercontent.com/user/abc123/raw/abc/file.md"
    r: GitHubUrl = GitHubUrl(url)
    assert r.get_raw_url() == url


def test_gist_url_str() -> None:
    url: str = "https://gist.githubusercontent.com/user/abc123/raw/abc/file.md"
    r: GitHubUrl = GitHubUrl(url)
    assert str(r) == url


def test_github_blob_md_url_parses_remote() -> None:
    url: str = "https://github.com/user/repo/blob/main/folder/file.md"
    r: GitHubUrl = GitHubUrl(url)
    assert r.url_structure is not None
    assert r.url_structure.user == "user"
    assert r.url_structure.repo == "repo"
    assert r.url_structure.branch == "main"
    assert r.url_structure.relative_path == "folder/file.md"


def test_github_blob_md_get_raw_url() -> None:
    url: str = "https://github.com/user/repo/blob/main/folder/file.md"
    r: GitHubUrl = GitHubUrl(url)
    assert r.get_raw_url() == "https://raw.githubusercontent.com/user/repo/main/folder/file.md"


def test_github_blob_md_str() -> None:
    url: str = "https://github.com/user/repo/blob/main/folder/file.md"
    r: GitHubUrl = GitHubUrl(url)
    assert str(r) == "https://raw.githubusercontent.com/user/repo/main/folder/file.md"


def test_github_tree_url_parses_remote() -> None:
    url: str = "https://github.com/user/repo/tree/main/folder/sub"
    r: GitHubUrl = GitHubUrl(url)
    assert r.url_structure is not None
    assert r.url_structure.user == "user"
    assert r.url_structure.repo == "repo"
    assert r.url_structure.branch == "main"
    assert r.url_structure.relative_path == "folder/sub"


def test_invalid_github_url_raises_warning() -> None:
    with pytest.raises(Warning):
        GitHubUrl("https://github.com/user/repo/invalid/path/file.md")


def test_github_blob_nested_folder() -> None:
    url: str = "https://github.com/user/repo/blob/main/a/b/c/file.md"
    r: GitHubUrl = GitHubUrl(url)
    assert r.url_structure is not None
    assert r.url_structure.relative_path == "a/b/c/file.md"
    assert r.get_raw_url() == "https://raw.githubusercontent.com/user/repo/main/a/b/c/file.md"
