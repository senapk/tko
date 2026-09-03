from pathlib import Path
from typing import cast

from tko.repository.git_cache import GitCache
from tko.repository.remote import Source
from tko.repository.remote_resolver import SourceResolver


class FakeGitCache:
    def __init__(self, repository: Path, found: bool):
        self.repository = repository
        self.found = found

    def get_repository_dir(self, _url: str, load_git: bool) -> tuple[Path, bool]:
        assert load_git is True
        return self.repository, self.found


def make_source() -> Source:
    source = Source.from_git_file(
        "disc",
        "https://github.com/user/course",
        branch="main",
        index="README.md",
    )
    assert source is not None
    return source


def test_remote_index_is_copied_to_materialized_source(tmp_path: Path) -> None:
    cached = tmp_path / "cache"
    cached.mkdir()
    (cached / "README.md").write_text("# cached index\n", encoding="utf-8")
    resolver = SourceResolver(cast(GitCache, FakeGitCache(cached, True)), tmp_path)

    index, found = resolver.resolve_index_file(make_source(), load_git=True)

    assert found is True
    assert index == tmp_path / "disc" / "README.md"
    assert index.read_text(encoding="utf-8") == "# cached index\n"


def test_remote_index_refreshes_existing_materialized_snapshot(tmp_path: Path) -> None:
    cached = tmp_path / "cache"
    cached.mkdir()
    (cached / "README.md").write_text("# new index\n", encoding="utf-8")
    snapshot = tmp_path / "disc" / "README.md"
    snapshot.parent.mkdir()
    snapshot.write_text("# old index\n", encoding="utf-8")
    resolver = SourceResolver(cast(GitCache, FakeGitCache(cached, True)), tmp_path)

    index, found = resolver.resolve_index_file(make_source(), load_git=True)

    assert found is True
    assert index == snapshot
    assert snapshot.read_text(encoding="utf-8") == "# new index\n"


def test_offline_remote_source_uses_materialized_snapshot(tmp_path: Path) -> None:
    snapshot = tmp_path / "disc" / "README.md"
    snapshot.parent.mkdir()
    snapshot.write_text("# offline index\n", encoding="utf-8")
    resolver = SourceResolver(cast(GitCache, FakeGitCache(tmp_path / "missing-cache", False)), tmp_path)

    index, found = resolver.resolve_index_file(make_source(), load_git=True)

    assert found is True
    assert index == snapshot


def test_remote_source_without_cache_or_snapshot_is_unavailable(tmp_path: Path) -> None:
    resolver = SourceResolver(cast(GitCache, FakeGitCache(tmp_path / "missing-cache", False)), tmp_path)

    index, found = resolver.resolve_index_file(make_source(), load_git=True)

    assert found is False
    assert index == tmp_path / "disc" / "README.md"
