from pathlib import Path
from typing import Any, cast

from tko.repository.repository_data import RepositoryData
from tko.repository.remote import Source


def make_source(name: str, target: str = "base") -> Source:
    return Source.from_local_file(name, Path(target), is_editable=False)


def test_set_get_and_replace_source(tmp_path: Path) -> None:
    data = RepositoryData(tmp_path)
    source_a = make_source("a")
    source_b = make_source("b")

    data.set_source(source_a)
    data.set_source(source_b)

    assert data.get_source("a") == Source.from_local_file("a", Path("base"), is_editable=True)
    assert data.get_source("b") == Source.from_local_file("b", Path("base"), is_editable=True)
    assert data.get_source("missing") is None

    replaced_a = make_source("a", "alt")
    data.set_source(replaced_a)
    assert data.get_source("a") == Source.from_local_file("a", Path("alt"), is_editable=True)


def test_get_sources_uses_labs_authoring_source_by_default(tmp_path: Path) -> None:
    data = RepositoryData(tmp_path)
    data.set_source(make_source("source1"))
    data.set_source(make_source("source2"))

    sources = data.get_sources()

    assert sources["labs"].name == "labs"
    assert data.authoring_source == "labs"
    assert [source.name for source in sources.values() if source.name != "labs"] == ["source1", "source2"]


def test_load_from_dict_loads_current_profile_and_state(tmp_path: Path) -> None:
    data = RepositoryData(tmp_path)
    payload: dict[str, Any] = {
        "version": "0.2",
        "profile": {
            "authoring_source": "labs",
            "sources": {"labs": {"uri": "README.md"}, "disc": {"uri": "material/README.md"}},
            "audit": {"enabled": True, "interval_seconds": 120},
        },
        "preferences": {"show_time": "true", "lang": "py"},
        "state": {"expanded": ["q1", "q2"], "selected": "repo@task", "selected_index": 4},
    }

    data.load_from_dict(payload)

    assert data.version == "0.2"
    assert data.expanded == ["q1", "q2"]
    assert data.flags == {"show_time": "true"}
    assert data.audit_enabled is True
    assert data.audit_interval_seconds == 120
    assert data.lang == "py"
    assert data.selected == "repo@task"
    assert data.selected_index == 4
    loaded_source = data.get_source("disc")
    assert loaded_source is not None
    assert loaded_source.path_or_url == "material/README.md"


def test_load_from_dict_ignores_wrong_types_and_does_not_raise(tmp_path: Path) -> None:
    data = RepositoryData(tmp_path)
    data.version = "1.0"
    data.load_from_dict({"version": 123, "sources": "invalid"})

    assert data.version == "1.0"
    assert data.get_source("labs") is not None


def test_save_to_dict_exports_current_state(tmp_path: Path) -> None:
    data = RepositoryData(tmp_path)
    source = make_source("disc")
    data.set_source(source)
    data.version = "0.2"
    data.expanded = ["q1"]
    data.flags = {"panel": "logs"}
    data.audit_enabled = True
    data.profile_language = "cpp"
    data.lang = "cpp"
    data.selected = "disc@task1"
    data.selected_index = 2

    saved = cast(dict[str, Any], data.to_dict())

    assert saved["version"] == "0.2"
    assert saved["profile"]["authoring_source"] == "labs"
    assert saved["profile"]["language"] == "cpp"
    assert saved["profile"]["audit"] == {"enabled": True, "interval_seconds": None}
    assert saved["preferences"] == {"panel": "logs"}
    assert saved["state"] == {"expanded": ["q1"], "selected": "disc@task1", "selected_index": 2}
    sources = cast(dict[str, dict[str, str]], saved["profile"]["sources"])
    assert sources["disc"] == {"uri": "base"}
