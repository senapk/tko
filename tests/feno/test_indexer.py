from pathlib import Path

import pytest

from tko.feno.indexer import TaskLine
from tko.util.console import Console


def test_index_line_accepts_windows_separator_for_readme(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    base_dir = tmp_path

    line = "- [ ] `@user_001 eval=none` [Sample](user_001\\README.md)"
    tl = TaskLine(index_path=index_path, base_dir=base_dir)
    parsed = tl.init_by_line(line)

    assert parsed is True
    assert tl.key == "user_001"
    assert tl.target_file == (index_path.parent / "user_001" / "README.md").resolve()


def test_local_task_key_defaults_to_relative_activity_path(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    base_dir = tmp_path
    task_dir = base_dir / "labs" / "carro"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Carro\n", encoding="utf-8")

    line = TaskLine(index_path=index_path, base_dir=base_dir)
    assert line.init_by_line("- [ ] `eval=none` [Carro](labs/carro/README.md)") is True
    assert line.key == "labs/carro"


def test_fix_readme_normalizes_managed_key_to_local_path(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    task_dir = tmp_path / "labs" / "sum"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Sum\n", encoding="utf-8")
    index_path.write_text(
        "- [ ] `@wrong eval=none` [Sum](labs/sum/README.md)\n", encoding="utf-8"
    )
    fix_readme(index_path, tmp_path / "labs", verbose=False, warn_key_path_mismatches=True)

    content = index_path.read_text(encoding="utf-8")
    assert "[Sum](labs/sum/README.md)" in content
    assert "@wrong" not in content


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
        "- [ ] `@t1 eval=none` [Tarefa Um](base/t1/README.md)\n"
        "- [ ] `@t_broken eval=none` [Quebrada](base/t_broken/README.md)\n"
    )
    index_path.write_text(original_content, encoding="utf-8")

    fix_readme(index=index_path, base_dir=base_dir, verbose=False, yes=True)

    content = index_path.read_text(encoding="utf-8")
    assert "[Tarefa Um](base/t1/README.md)" in content
    assert "@t_broken" not in content


def test_fix_readme_interactive_keeps_broken_local_target_when_user_declines(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    index_path.write_text(
        "# Disciplina\n\n"
            "- [ ] `@t_broken eval=none` [Quebrada](base/t_broken/README.md)\n",
        encoding="utf-8",
    )

    def decline_removal(_prompt: str = "") -> str:
        return "n"

    monkeypatch.setattr("builtins.input", decline_removal)

    fix_readme(index=index_path, base_dir=base_dir, verbose=True)

    assert "[Quebrada](base/t_broken/README.md)" in index_path.read_text(encoding="utf-8")
    assert "@t_broken" not in index_path.read_text(encoding="utf-8")


def test_fix_readme_interactive_removes_broken_local_target_when_user_confirms(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    index_path.write_text(
        "# Disciplina\n\n"
            "- [ ] `@t_broken eval=none` [Quebrada](base/t_broken/README.md)\n",
        encoding="utf-8",
    )

    def confirm_removal(_prompt: str = "") -> str:
        return "s"

    monkeypatch.setattr("builtins.input", confirm_removal)

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
    assert "[Tarefa Um](base/t1/README.md)" in content
    # t2 should be auto-added
    assert "[Tarefa Dois](base/t2/README.md)" in content
    assert "Tarefa Dois" in content


def test_fix_readme_does_not_duplicate_source_prefixed_task_keys(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "labs"
    task_dir = base_dir / "new_task"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# New task\n", encoding="utf-8")
    index_path.write_text("# labs\n", encoding="utf-8")

    fix_readme(index_path, base_dir, verbose=False)
    fix_readme(index_path, base_dir, verbose=False)

    content = index_path.read_text(encoding="utf-8")
    assert content.count("[New task](labs/new_task/README.md)") == 1


def test_fix_readme_removes_existing_duplicate_local_task(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "labs"
    task_dir = base_dir / "new_task"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# New task\n", encoding="utf-8")
    task_line = "- [ ] `@labs/new_task eval=diff` [New task](labs/new_task/README.md)\n"
    index_path.write_text(f"# labs\n\n## labs\n\n{task_line}{task_line}", encoding="utf-8")

    fix_readme(index_path, base_dir, verbose=False)

    assert index_path.read_text(encoding="utf-8").count("[New task](labs/new_task/README.md)") == 1


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
        "- [ ] `@t1 gain=2 cost=2 size=1 eval=self` [Tarefa Um](base/t1/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index=index_path, base_dir=base_dir, verbose=False)

    content = index_path.read_text(encoding="utf-8")
    assert "eval=self" in content
    assert "gain=2 cost=2 size=1" in content


def test_fix_readme_uses_canonical_defaults_and_aligned_columns(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    task_dir = base_dir / "long_task"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Tarefa Nova\n", encoding="utf-8")
    index_path.write_text("# Curso\n", encoding="utf-8")

    fix_readme(index_path, base_dir, verbose=False)

    line = next(line for line in index_path.read_text(encoding="utf-8").splitlines() if "long_task/README.md" in line)
    assert "eval=diff" in line
    assert "gcs=" not in line
    assert "📖" not in line and "🛠" not in line


def test_fix_readme_can_skip_column_alignment(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    for key in ("a", "long_task"):
        task_dir = base_dir / key
        task_dir.mkdir(parents=True)
        (task_dir / "README.md").write_text(f"# {key}\n", encoding="utf-8")
    index_path.write_text(
        "- [ ] `@a eval=none` [A](base/a/README.md)\n"
        "- [ ] `@long_task eval=diff gain=2` [Long](base/long_task/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index_path, base_dir, verbose=False, align=False)

    task_lines = [line for line in index_path.read_text(encoding="utf-8").splitlines() if line.startswith("- [")]
    assert "`eval=none`" in task_lines[0]
    assert "`eval=diff gain=2`" in task_lines[1]


def test_fix_readme_aligns_columns_by_default(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    for key in ("a", "long_task"):
        task_dir = base_dir / key
        task_dir.mkdir(parents=True)
        (task_dir / "README.md").write_text(f"# {key}\n", encoding="utf-8")
    index_path.write_text(
        "- [ ] `@a eval=none` [A](base/a/README.md)\n"
        "- [ ] `@long_task eval=diff gain=20` [Long](base/long_task/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index_path, base_dir, verbose=False)

    task_lines = [line for line in index_path.read_text(encoding="utf-8").splitlines() if line.startswith("- [")]
    assert "@base/a" not in task_lines[0] and "eval=none" in task_lines[0] and "gcs=" not in task_lines[0]
    assert "@base/long_task" not in task_lines[1] and "eval=diff gain=20" in task_lines[1]


@pytest.mark.parametrize(
    ("eval_mode", "has_tests", "expected"),
    [
        ("self", True, "possui testes"),
        ("self", False, None),
        ("diff", True, None),
        ("diff", False, "não possui testes"),
    ],
)
def test_fix_readme_warns_when_eval_mode_does_not_match_tests(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    eval_mode: str,
    has_tests: bool,
    expected: str | None,
) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    task_dir = base_dir / "task"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Tarefa\n", encoding="utf-8")
    index_path.write_text(
        f"- [ ] `@task eval={eval_mode}` [Tarefa](base/task/README.md)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("tko.feno.indexer.TestsFinder.find_tests", lambda _folder: has_tests)

    with Console.capture() as capture:
        fix_readme(index_path, base_dir, verbose=True)

    output = capture.getvalue()
    if expected is None:
        assert "Aviso:" not in output
    else:
        assert expected in output


def test_fix_readme_checks_materialized_external_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    materialized = tmp_path / "remote-task"
    materialized.mkdir()
    (materialized / "README.md").write_text("# Remota\n", encoding="utf-8")
    index_path.write_text(
        "- [ ] `@remote-task eval=diff` [Remota](https://github.com/user/repo/blob/main/README.md)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("tko.feno.indexer.TestsFinder.find_tests", lambda _folder: False)

    with Console.capture() as capture:
        fix_readme(index_path, tmp_path, verbose=True)

    assert "não possui testes" in capture.getvalue()
    assert "@remote-task" in index_path.read_text(encoding="utf-8")


def test_fix_readme_preserves_materialized_task_source_comment(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    task_dir = tmp_path / "labs" / "fila"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Fila\n", encoding="utf-8")
    source = "https://github.com/org/repo/blob/main/labs/fila/README.md"
    index_path.write_text(
        "- [ ] `@old eval=diff` [Fila](labs/fila/README.md) "
        f"<!-- source: {source} -->\n",
        encoding="utf-8",
    )

    fix_readme(index_path, tmp_path / "labs", verbose=False)
    fix_readme(index_path, tmp_path / "labs", verbose=False)

    content = index_path.read_text(encoding="utf-8")
    assert "[Fila](labs/fila/README.md)" in content
    assert "@old" not in content
    assert content.count(f"<!-- source={source} -->") == 1


def test_fix_readme_preserves_none_fields(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()
    task_dir = base_dir / "reading"
    task_dir.mkdir()
    (task_dir / "README.md").write_text("# Leitura\n", encoding="utf-8")
    index_path.write_text(
        "- [ ] `@reading gain=4 cost=3 size=2 eval=none` [Leitura](base/reading/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index_path, base_dir, verbose=False)

    line = next(line for line in index_path.read_text(encoding="utf-8").splitlines() if "base/reading/README.md" in line)
    assert "eval=none gain=4 cost=3 size=2" in line


def test_fix_readme_preserves_yaml_front_matter_and_variable_fields(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    task_dir = base_dir / "task"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Task\n", encoding="utf-8")
    index_path.write_text(
        "---\nargs: [value, depth]\nexpr: \"value * depth\"\n---\n"
        "- [ ] `@task value=3 depth=2 eval=diff` [Task](base/task/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index_path, base_dir, verbose=False, align=False)

    content = index_path.read_text(encoding="utf-8")
    assert "args: [value, depth]" in content
    assert 'expr: "value * depth"' in content
    assert "`eval=diff value=3 depth=2`" in content


def test_fix_readme_removes_quest_xpgoal(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    for task in ["soma", "media", "desafio"]:
        task_dir = base_dir / task
        task_dir.mkdir(parents=True)
        (task_dir / "README.md").write_text(f"# {task.title()}\n", encoding="utf-8")

    index_path.write_text(
        "# Curso\n\n"
        "## Vetores <!-- key=@vetores xpgoal=99 -->\n\n"
        "- [x] `@soma gain=2 cost=1 size=1 eval=diff` [Soma](base/soma/README.md)\n"
        "- [x] `@media gain=3 cost=1 size=1 eval=diff` [Media](base/media/README.md)\n"
        "- [ ] `@desafio gain=5 cost=3 size=2 eval=diff` [Desafio](base/desafio/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index_path, base_dir, verbose=False)

    content = index_path.read_text(encoding="utf-8")
    assert "## Vetores <!-- @vetores -->" in content
    assert "xpgoal=" not in content
    assert "- [x]" in content


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
    line.init_by_line("- [ ] `@task eval=none` [Título antigo](task/README.md)")
    elements.lines = ["texto", line]
    elements.fix_titles(load_titles=True)

    assert line.tm.title == "Título do arquivo"
