from pathlib import Path
from typing import Any, cast

import pytest

from tko.run.wdir_target_resolver import WdirTargetResolver


class _FakeLangSettings:
    def get_languages_with_drafts(self) -> dict[str, str]:
        return {"py": "", "cpp": ""}


class _FakeSettings:
    def get_languages_settings(self) -> _FakeLangSettings:
        return _FakeLangSettings()


def _resolver() -> WdirTargetResolver:
    return WdirTargetResolver(cast(Any, _FakeSettings()))


def test_normalize_targets_injects_current_dir_when_empty():
    resolver = _resolver()

    normalized = resolver.normalize_targets([])

    assert normalized == [Path()]


def test_get_autoload_folder_detects_single_directory_target(tmp_path: Path):
    resolver = _resolver()

    folder = resolver.get_autoload_folder([tmp_path])

    assert folder == tmp_path


def test_resolve_explicit_targets_splits_sources_and_solvers(tmp_path: Path):
    resolver = _resolver()
    source_tio = tmp_path / "cases.tio"
    source_md = tmp_path / "cases.md"
    solver_py = tmp_path / "solver.py"
    source_tio.write_text("", encoding="utf-8")
    source_md.write_text("", encoding="utf-8")
    solver_py.write_text("", encoding="utf-8")

    sources, solvers = resolver.resolve_explicit_targets([source_tio, source_md, solver_py])

    assert sources == [source_tio, source_md]
    assert solvers == [solver_py]


def test_resolve_explicit_targets_raises_when_target_missing(tmp_path: Path):
    resolver = _resolver()
    missing = tmp_path / "missing.tio"

    with pytest.raises(Warning, match="não encontrado"):
        resolver.resolve_explicit_targets([missing])


def test_resolve_autoload_collects_sources_and_sorted_solvers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    resolver = _resolver()
    (tmp_path / "a.tio").write_text("", encoding="utf-8")
    (tmp_path / "b.vpl").write_text("", encoding="utf-8")
    (tmp_path / "c.toml").write_text("", encoding="utf-8")
    (tmp_path / "d.md").write_text("", encoding="utf-8")

    class _FakeFinder:
        def __init__(self, folder: Path, lang: str):
            self.folder = folder
            self.lang = lang

        def load_source_files(self, extra: list[str] | None = None) -> list[Path]:
            _ = extra
            return [self.folder / "z.py", self.folder / "a.py"]

    monkeypatch.setattr("tko.run.wdir_target_resolver.DraftsFinderCached", _FakeFinder)

    sources, solvers = resolver.resolve_autoload(tmp_path, "")

    assert set([path.name for path in sources]) == {"a.tio", "b.vpl", "c.toml", "d.md"}
    assert [path.name for path in solvers] == ["a.py", "z.py"]
