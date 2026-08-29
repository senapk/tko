from pathlib import Path

import pytest

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


def test_fix_readme_yes_removes_broken_local_target(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    # Create task 1: valid
    t1_dir = base_dir / "t1"
    t1_dir.mkdir()
    (t1_dir / "README.md").write_text("# Tarefa Um\n\nDescricao", encoding="utf-8")

    original_content = (
        "# Disciplina\n\n"
        "## Secao <!-- @sec -->\n\n"
        "- [ ] `@t1` [Tarefa Um](base/t1/README.md)\n"
        "- [ ] `@t_broken` [Quebrada](base/t_broken/README.md)\n"
    )
    index_path.write_text(original_content, encoding="utf-8")

    fix_readme(index=index_path, base_dir=base_dir, verbose=False, yes=True)

    content = index_path.read_text(encoding="utf-8")
    assert "@t1" in content
    assert "@t_broken" not in content


def test_fix_readme_interactive_keeps_broken_local_target_when_user_declines(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    index_path.write_text(
        "# Disciplina\n\n"
        "- [ ] `@t_broken` [Quebrada](base/t_broken/README.md)\n",
        encoding="utf-8",
    )

    monkeypatch.setattr("builtins.input", lambda _prompt: "n")

    fix_readme(index=index_path, base_dir=base_dir, verbose=True)

    assert "@t_broken" in index_path.read_text(encoding="utf-8")


def test_fix_readme_interactive_removes_broken_local_target_when_user_confirms(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    index_path.write_text(
        "# Disciplina\n\n"
        "- [ ] `@t_broken` [Quebrada](base/t_broken/README.md)\n",
        encoding="utf-8",
    )

    monkeypatch.setattr("builtins.input", lambda _prompt: "s")

    fix_readme(index=index_path, base_dir=base_dir, verbose=True)

    assert "@t_broken" not in index_path.read_text(encoding="utf-8")


def test_fix_readme_indexes_new_dirs(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    # Create task 1: valid
    t1_dir = base_dir / "t1"
    t1_dir.mkdir()
    (t1_dir / "README.md").write_text("# Tarefa Um\n\nDescricao", encoding="utf-8")

    # Create task 2: new, not indexed yet
    t2_dir = base_dir / "t2"
    t2_dir.mkdir()
    (t2_dir / "README.md").write_text("# Tarefa Dois\n\nDescricao", encoding="utf-8")

    index_path.write_text(
        "# Disciplina\n\n"
        "## Secao <!-- @sec -->\n\n"
        "- [ ] `@t1` [Tarefa Um](base/t1/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index=index_path, base_dir=base_dir, verbose=False)

    content = index_path.read_text(encoding="utf-8")

    # t1 should be present with aligned tags
    assert "@t1" in content
    # t2 should be auto-added
    assert "@t2" in content
    assert "Tarefa Dois" in content


def test_fix_readme_preserves_eval_self(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    t1_dir = base_dir / "t1"
    t1_dir.mkdir()
    (t1_dir / "README.md").write_text("# Tarefa Um\n\nDescricao", encoding="utf-8")

    index_path.write_text(
        "## Secao <!-- @sec -->\n\n"
        "- [ ] `@t1 gain=2 hard=2 size=1 type=make eval=self` [Tarefa Um](base/t1/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index=index_path, base_dir=base_dir, verbose=False)

    content = index_path.read_text(encoding="utf-8")
    assert "eval=self" in content
    assert "gain=2" in content
    assert "hard=2" in content


def test_fix_readme_uses_canonical_defaults_and_aligned_columns(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    task_dir = base_dir / "long_task"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Tarefa Nova\n", encoding="utf-8")
    index_path.write_text("# Curso\n", encoding="utf-8")

    fix_readme(index_path, base_dir, verbose=False)

    line = next(line for line in index_path.read_text(encoding="utf-8").splitlines() if "@long_task" in line)
    assert "gain=1 hard=1 size=1 type=make eval=test" in line
    assert "📖" not in line and "🛠" not in line


def test_fix_titles_checks_tasks_after_non_task_lines(tmp_path: Path) -> None:
    from tko.feno.indexer import Elements

    index_path = tmp_path / "README.md"
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    (task_dir / "README.md").write_text("# Título do arquivo\n", encoding="utf-8")
    index_path.write_text("# Curso\n", encoding="utf-8")

    elements = Elements(index_path, tmp_path, verbose=False)
    elements.load_lines()
    line = TaskLine(index_path, tmp_path)
    line.init_by_line("- [ ] `@task` [Título antigo](task/README.md)")
    elements.lines = ["texto", line]
    elements.fix_titles(load_titles=True)

    assert line.tm.title == "Título do arquivo"
