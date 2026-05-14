from pathlib import Path
from typing import Any, cast

from tko.repository.repository_data import RepositoryData
from tko.repository.remote import Remote


def make_source(name: str, target: str = "base") -> Remote:
    remote = Remote(name)
    remote.data.name = name
    remote.data.set_local_source(Path(target), is_editable=False)
    return remote


def test_set_get_and_delete_source(tmp_path: Path) -> None:
    _ = tmp_path
    data = RepositoryData()
    source_a = make_source("a")
    source_b = make_source("b")

    data.set_remote(source_a)
    data.set_remote(source_b)

    assert data.get_remote("a") is source_a
    assert data.get_remote("b") is source_b
    assert data.get_remote("missing") is None

    replaced_a = make_source("a", "alt")
    data.set_remote(replaced_a)
    assert data.get_remote("a") is replaced_a

    data.del_remote("b")
    assert data.get_remote("b") is None


def test_get_sources_ensures_sandbox_and_puts_it_first(tmp_path: Path) -> None:
    _ = tmp_path
    data = RepositoryData()
    data.set_remote(make_source("remote1"))
    data.set_remote(make_source("remote2"))

    sources = data.remotes_raw_list

    assert sources[0].data.name == ""
    assert [source.data.name for source in sources[1:]] == ["remote1", "remote2"]


def test_load_from_dict_loads_simple_fields_and_sources(tmp_path: Path) -> None:
    _ = tmp_path
    data = RepositoryData()
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
    loaded_source = data.get_remote("disc")
    assert loaded_source is not None
    assert loaded_source.data.target == "material"


def test_load_from_dict_ignores_wrong_types_and_does_not_raise(tmp_path: Path) -> None:
    _ = tmp_path
    data = RepositoryData()
    data.version = "1.0"
    data.load_from_dict({"version": 123, "sources": "invalid"})

    assert data.version == "1.0"
    assert data.get_remote("sandbox") is None


def test_save_to_dict_exports_current_state(tmp_path: Path) -> None:
    _ = tmp_path
    data = RepositoryData()
    source = make_source("disc")
    data.set_remote(source)
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