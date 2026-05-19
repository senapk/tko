from pathlib import Path
from typing import Any, cast

import pytest
from _pytest.monkeypatch import MonkeyPatch

import tko.repository.repository_loader as repository_loader_module
from tko.repository.repository import Repository
from tko.repository.repository_loader import ConfigMergeConflictError, RepositoryLoader


class FakePaths:
    def __init__(self, root: Path):
        self.root = root

    @property
    def config_file(self) -> Path:
        return self.root / ".tko" / "repository.yaml"

    @property
    def config_backup_file(self) -> Path:
        return Path(str(self.config_file) + ".backup")

    @property
    def cache_folder(self) -> Path:
        return self.root / ".tko" / "cache"


class FakeSource:
    def __init__(self):
        self.globals_args: tuple[Path, Path] | None = None

    def set_source_globals(self, root_workspace: Path, cache_folder: Path) -> None:
        self.globals_args = (root_workspace, cache_folder)


class FakeData:
    def __init__(self, sources: list[FakeSource] | None = None):
        self.flags: dict[str, Any] = {}
        self.loaded: dict[str, Any] | None = None
        self.version: str = ""
        self.saved_payload: dict[str, Any] = {"sources": [], "lang": ""}
        self.sources = sources or []

    def load_from_dict(self, data: dict[str, Any]) -> None:
        self.loaded = data
        self.flags = data.get("flags", {})

    def save_to_dict(self) -> dict[str, Any]:
        return self.saved_payload


class FakeFlags:
    def __init__(self):
        self.loaded: dict[str, Any] | None = None
        self.saved: dict[str, str] = {"show_time": "true"}

    def from_dict(self, data: dict[str, Any]) -> None:
        self.loaded = data

    def to_dict(self) -> dict[str, str]:
        return self.saved


class FakeRepo:
    def __init__(self, root: Path, sources: list[FakeSource] | None = None):
        self.paths = FakePaths(root)
        self.data = FakeData(sources)
        self.flags = FakeFlags()


def make_loader(root: Path, sources: list[FakeSource] | None = None) -> tuple[RepositoryLoader, FakeRepo]:
    repo = FakeRepo(root, sources)
    return RepositoryLoader(cast(Repository, repo)), repo


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_load_config_uses_main_file_and_sets_source_globals(tmp_path: Path):
    source = FakeSource()
    loader, repo = make_loader(tmp_path, [source])
    write_text(
        repo.paths.config_file,
        "flags:\n  panel: logs\nlang: py\nsources: []\n",
    )

    returned = loader.load_config()

    assert returned is loader
    assert repo.data.loaded == {"flags": {"panel": "logs"}, "lang": "py", "sources": []}
    assert repo.flags.loaded == {"panel": "logs"}
    assert source.globals_args is None


def test_load_config_falls_back_to_backup_when_main_file_is_empty(tmp_path: Path):
    loader, repo = make_loader(tmp_path)
    write_text(repo.paths.config_file, "")
    write_text(repo.paths.config_backup_file, "flags:\n  show_time: false\n")

    loader.load_config()

    assert repo.data.loaded == {"flags": {"show_time": False}}
    assert repo.flags.loaded == {"show_time": False}


def test_load_config_raises_for_merge_conflict(tmp_path: Path):
    loader, repo = make_loader(tmp_path)
    write_text(repo.paths.config_file, "<<<<<<< HEAD\nflags: {}\n=======\nflags: {}\n>>>>>>> branch\n")

    with pytest.raises(ConfigMergeConflictError):
        loader.load_config()


def test_load_config_raises_warning_for_invalid_yaml(tmp_path: Path):
    loader, repo = make_loader(tmp_path)
    write_text(repo.paths.config_file, "flags: [unterminated\n")

    with pytest.raises(Warning, match="contém erros de YAML"):
        loader.load_config()


def test_load_config_raises_warning_when_main_and_backup_are_empty(tmp_path: Path):
    loader, repo = make_loader(tmp_path)
    write_text(repo.paths.config_file, "")
    write_text(repo.paths.config_backup_file, "")

    with pytest.raises(Warning, match=r"está .*vazio"):
        loader.load_config()


def test_save_config_sets_version_and_writes_flags(monkeypatch: MonkeyPatch, tmp_path: Path):
    loader, repo = make_loader(tmp_path)
    repo.data.saved_payload = {"sources": [{"name": "sandbox"}], "lang": "py"}
    captured: dict[str, Any] = {}

    def fake_atomic_write_yaml(path: Path, payload: dict[str, Any]) -> None:
        captured["path"] = path
        captured["payload"] = payload

    monkeypatch.setattr(repository_loader_module, "atomic_write_yaml", fake_atomic_write_yaml)

    returned = loader.save_config()

    assert returned.repo is repo
    assert repo.data.version == "0.2"
    assert repo.data.flags == {"show_time": "true"}
    assert captured["path"] == repo.paths.config_file
    assert captured["payload"] == repo.data.saved_payload
    assert repo.paths.config_file.parent.exists()


def test_save_config_skips_write_when_payload_is_unchanged(monkeypatch: MonkeyPatch, tmp_path: Path):
    loader, repo = make_loader(tmp_path)
    repo.data.saved_payload = {"sources": [{"name": "sandbox"}], "lang": "py"}
    write_text(
        repo.paths.config_file,
        "sources:\n- name: sandbox\nlang: py\n",
    )
    loader.load_config()

    calls = {"count": 0}

    def fake_atomic_write_yaml(path: Path, payload: dict[str, Any]) -> None:
        calls["count"] += 1

    monkeypatch.setattr(repository_loader_module, "atomic_write_yaml", fake_atomic_write_yaml)

    returned = loader.save_config()

    assert returned.repo is repo
    assert repo.data.version == "0.2"
    assert repo.data.flags == {"show_time": "true"}
    assert calls["count"] == 0


def test_save_config_skips_write_when_only_selected_fields_change(monkeypatch: MonkeyPatch, tmp_path: Path):
    loader, repo = make_loader(tmp_path)
    repo.data.saved_payload = {
        "sources": [{"name": "sandbox"}],
        "lang": "py",
        "selected": "repo@q1@t1",
        "selected_index": 3,
    }
    write_text(
        repo.paths.config_file,
        "sources:\n- name: sandbox\nlang: py\nselected: repo@q1@t1\nselected_index: 3\n",
    )
    loader.load_config()
    repo.data.saved_payload = {
        "sources": [{"name": "sandbox"}],
        "lang": "py",
        "selected": "repo@q1@t2",
        "selected_index": 4,
    }

    calls = {"count": 0}

    def fake_atomic_write_yaml(path: Path, payload: dict[str, Any]) -> None:
        calls["count"] += 1

    monkeypatch.setattr(repository_loader_module, "atomic_write_yaml", fake_atomic_write_yaml)

    returned = loader.save_config()

    assert returned.repo is repo
    assert calls["count"] == 0


def test_save_config_writes_when_only_selected_fields_change_and_force_is_true(monkeypatch: MonkeyPatch, tmp_path: Path):
    loader, repo = make_loader(tmp_path)
    repo.data.saved_payload = {
        "sources": [{"name": "sandbox"}],
        "lang": "py",
        "selected": "repo@q1@t1",
        "selected_index": 3,
    }
    write_text(
        repo.paths.config_file,
        "sources:\n- name: sandbox\nlang: py\nselected: repo@q1@t1\nselected_index: 3\n",
    )
    loader.load_config()
    repo.data.saved_payload = {
        "sources": [{"name": "sandbox"}],
        "lang": "py",
        "selected": "repo@q1@t2",
        "selected_index": 4,
    }

    calls = {"count": 0}

    def fake_atomic_write_yaml(path: Path, payload: dict[str, Any]) -> None:
        calls["count"] += 1

    monkeypatch.setattr(repository_loader_module, "atomic_write_yaml", fake_atomic_write_yaml)

    returned = loader.save_config(force=True)

    assert returned.repo is repo
    assert calls["count"] == 1