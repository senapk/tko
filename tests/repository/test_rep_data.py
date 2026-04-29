from pathlib import Path
from typing import Any, cast

from tko.repository.git_cache import GitCache
from tko.repository.rep_data import RepData
from tko.repository.rep_source import RepSource


def make_git_cache(tmp_path: Path) -> GitCache:
    return GitCache(tmp_path / "cache")


def make_source(name: str, target: str = "base") -> RepSource:
    source = RepSource(name, git_cache=None)
    source.set_local_source(Path(target), writeable=False)
    return source


def test_set_get_and_delete_source(tmp_path: Path) -> None:
    data = RepData(make_git_cache(tmp_path))
    source_a = make_source("a")
    source_b = make_source("b")

    data.set_source(source_a)
    data.set_source(source_b)

    assert data.get_source("a") is source_a
    assert data.get_source("b") is source_b
    assert data.get_source("missing") is None

    replaced_a = make_source("a", "alt")
    data.set_source(replaced_a)
    assert data.get_source("a") is replaced_a

    data.del_source("b")
    assert data.get_source("b") is None


def test_get_sources_ensures_sandbox_and_puts_it_first(tmp_path: Path) -> None:
    data = RepData(make_git_cache(tmp_path))
    data.set_source(make_source("remote1"))
    data.set_source(make_source("remote2"))

    sources = data.get_sources()

    assert sources[0].name == "sandbox"
    assert [source.name for source in sources[1:]] == ["remote1", "remote2"]


def test_load_from_dict_loads_simple_fields_and_sources(tmp_path: Path) -> None:
    data = RepData(make_git_cache(tmp_path))
    payload: dict[str, Any] = {
        "version": "0.2",
        "expanded": ["q1", "q2"],
        "flags": {"show_time": "true"},
        "lang": "py",
        "selected": "repo@task",
        "selected_index": 4,
        "sources": [
            {
                "name": "disc",
                "target": "material",
                "type": "local",
                "writeable": False,
                "index": "README.md",
            }
        ],
    }

    data.load_from_dict(payload)

    assert data.version == "0.2"
    assert data.expanded == ["q1", "q2"]
    assert data.flags == {"show_time": "true"}
    assert data.lang == "py"
    assert data.selected == "repo@task"
    assert data.selected_index == 4
    loaded_source = data.get_source("disc")
    assert loaded_source is not None
    assert loaded_source.target == "material"


def test_load_from_dict_ignores_wrong_types_and_does_not_raise(tmp_path: Path) -> None:
    data = RepData(make_git_cache(tmp_path))
    data.version = "1.0"
    data.load_from_dict({"version": 123, "sources": "invalid"})

    assert data.version == "1.0"
    assert data.get_source("sandbox") is None


def test_save_to_dict_exports_current_state(tmp_path: Path) -> None:
    data = RepData(make_git_cache(tmp_path))
    source = make_source("disc")
    data.set_source(source)
    data.version = "0.2"
    data.expanded = ["q1"]
    data.flags = {"panel": "logs"}
    data.lang = "cpp"
    data.selected = "disc@task1"
    data.selected_index = 2

    saved = data.save_to_dict()

    assert saved["version"] == "0.2"
    assert saved["expanded"] == ["q1"]
    assert saved["flags"] == {"panel": "logs"}
    assert saved["lang"] == "cpp"
    assert saved["selected"] == "disc@task1"
    assert saved["selected_index"] == 2
    assert isinstance(saved["sources"], list)
    sources = cast(list[dict[str, Any]], saved["sources"])
    assert len(sources) == 1
    assert sources[0]["name"] == "disc"