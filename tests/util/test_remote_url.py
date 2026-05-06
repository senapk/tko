import pytest
from tko.util.remote_url import RemoteUrl


def test_url_without_https_raises_value_error() -> None:
    with pytest.raises(ValueError):
        RemoteUrl("http://github.com/user/repo/blob/main/folder/file.md")


def test_url_without_scheme_raises_value_error() -> None:
    with pytest.raises(ValueError):
        RemoteUrl("github.com/user/repo/blob/main/folder/file.md")


def test_gist_url_sets_raw_link() -> None:
    url: str = "https://gist.githubusercontent.com/user/abc123/raw/abc/file.md"
    r: RemoteUrl = RemoteUrl(url)
    assert r.raw_link == url
    assert r.remote is None


def test_gist_url_get_raw_url() -> None:
    url: str = "https://gist.githubusercontent.com/user/abc123/raw/abc/file.md"
    r: RemoteUrl = RemoteUrl(url)
    assert r.get_raw_url() == url


def test_gist_url_str() -> None:
    url: str = "https://gist.githubusercontent.com/user/abc123/raw/abc/file.md"
    r: RemoteUrl = RemoteUrl(url)
    assert str(r) == url


def test_github_blob_md_url_parses_remote() -> None:
    url: str = "https://github.com/user/repo/blob/main/folder/file.md"
    r: RemoteUrl = RemoteUrl(url)
    assert r.remote is not None
    assert r.remote.user == "user"
    assert r.remote.repo == "repo"
    assert r.remote.branch == "main"
    assert r.remote.folder == "folder"
    assert r.remote.file == "file.md"


def test_github_blob_md_get_raw_url() -> None:
    url: str = "https://github.com/user/repo/blob/main/folder/file.md"
    r: RemoteUrl = RemoteUrl(url)
    assert r.get_raw_url() == "https://raw.githubusercontent.com/user/repo/main/folder/file.md"


def test_github_blob_md_str() -> None:
    url: str = "https://github.com/user/repo/blob/main/folder/file.md"
    r: RemoteUrl = RemoteUrl(url)
    assert str(r) == "https://raw.githubusercontent.com/user/repo/main/folder/file.md"


def test_github_tree_url_parses_remote() -> None:
    url: str = "https://github.com/user/repo/tree/main/folder/sub"
    r: RemoteUrl = RemoteUrl(url)
    assert r.remote is not None
    assert r.remote.user == "user"
    assert r.remote.repo == "repo"
    assert r.remote.branch == "main"
    assert r.remote.folder == "folder/sub"


def test_invalid_github_url_raises_warning() -> None:
    with pytest.raises(Warning):
        RemoteUrl("https://github.com/user/repo/invalid/path/file.md")


def test_github_blob_nested_folder() -> None:
    url: str = "https://github.com/user/repo/blob/main/a/b/c/file.md"
    r: RemoteUrl = RemoteUrl(url)
    assert r.remote is not None
    assert r.remote.folder == "a/b/c"
    assert r.remote.file == "file.md"
    assert r.get_raw_url() == "https://raw.githubusercontent.com/user/repo/main/a/b/c/file.md"
