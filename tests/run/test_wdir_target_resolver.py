from pathlib import Path


import pytest

from tko.run.wdir_target_resolver import WdirTargetResolver





def _resolver() -> WdirTargetResolver:
    return WdirTargetResolver()


def test_normalize_targets_injects_current_dir_when_empty():
    resolver = _resolver()

    normalized = resolver.normalize_targets([])

    assert normalized == [Path()]





def test_identify_source_and_solver_targets(tmp_path: Path):
    resolver = _resolver()
    source_tio = tmp_path / "cases.tio"
    source_md = tmp_path / "cases.md"
    solver_py = tmp_path / "solver.py"
    source_tio.write_text("", encoding="utf-8")
    source_md.write_text("", encoding="utf-8")
    solver_py.write_text("", encoding="utf-8")

    sources, solvers = resolver.identify_source_and_solver_targets([source_tio, source_md, solver_py])

    assert sources == [source_tio, source_md]
    assert solvers == [solver_py]


def test_identify_source_and_solver_targets_raises_when_target_missing(tmp_path: Path):
    resolver = _resolver()
    missing = tmp_path / "missing.tio"

    with pytest.raises(Warning, match="não encontrado"):
        resolver.identify_source_and_solver_targets([missing])


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
