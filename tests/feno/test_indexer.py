from pathlib import Path

from tko.feno.indexer import TaskLine


def test_index_line_accepts_windows_separator_for_readme(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    base_dir = tmp_path

    line = "- [ ] `@user_001` [Sample](user_001\\README.md)"
    tl = TaskLine(index_path=index_path, base_dir=base_dir)
    parsed = tl.init_by_line(line)

    assert parsed is True
    assert tl.tm.key == "user_001"
    assert tl.target_file == (index_path.parent / "user_001" / "README.md").resolve()
