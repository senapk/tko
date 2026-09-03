from pathlib import Path

import pytest

from tko.feno.indexer import TaskLine
from tko.util.console import Console


def test_index_line_accepts_windows_separator_for_readme(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    base_dir = tmp_path

    line = "- [ ] `@user_001 type=wiki` [Sample](user_001\\README.md)"
    tl = TaskLine(index_path=index_path, base_dir=base_dir)
    parsed = tl.init_by_line(line)

    assert parsed is True
    assert tl.tm.key == "user_001"
    assert tl.target_file == (index_path.parent / "user_001" / "README.md").resolve()


def test_local_task_key_defaults_to_relative_activity_path(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    base_dir = tmp_path
    task_dir = base_dir / "labs" / "carro"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# Carro\n", encoding="utf-8")

    line = TaskLine(index_path=index_path, base_dir=base_dir)
    assert line.init_by_line("- [ ] `type=wiki` [Carro](labs/carro/README.md)") is True
    assert line.key == "labs/carro"


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
        "- [ ] `@t1 type=wiki` [Tarefa Um](base/t1/README.md)\n"
        "- [ ] `@t_broken type=wiki` [Quebrada](base/t_broken/README.md)\n"
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
            "- [ ] `@t_broken type=wiki` [Quebrada](base/t_broken/README.md)\n",
        encoding="utf-8",
    )

    def decline_removal(_prompt: str = "") -> str:
        return "n"

    monkeypatch.setattr("builtins.input", decline_removal)

    fix_readme(index=index_path, base_dir=base_dir, verbose=True)

    assert "@t_broken" in index_path.read_text(encoding="utf-8")


def test_fix_readme_interactive_removes_broken_local_target_when_user_confirms(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    index_path.write_text(
        "# Disciplina\n\n"
            "- [ ] `@t_broken type=wiki` [Quebrada](base/t_broken/README.md)\n",
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
    assert "@t1" in content
    # t2 should be auto-added
    assert "@base/t2" in content
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
        "- [ ] `@t1 gain=2 hard=2 size=1 type=self` [Tarefa Um](base/t1/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index=index_path, base_dir=base_dir, verbose=False)

    content = index_path.read_text(encoding="utf-8")
    assert "type=self" in content
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

    line = next(line for line in index_path.read_text(encoding="utf-8").splitlines() if "@base/long_task" in line)
    assert "type=diff gain=1 hard=1 size=1" in line
    assert "📖" not in line and "🛠" not in line


@pytest.mark.parametrize(
    ("task_type", "has_tests", "expected"),
    [
        ("self", True, "possui testes"),
        ("self", False, None),
        ("diff", True, None),
        ("diff", False, "não possui testes"),
    ],
)
def test_fix_readme_warns_when_task_type_does_not_match_tests(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    task_type: str,
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
        f"- [ ] `@task type={task_type}` [Tarefa](base/task/README.md)\n",
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
        "- [ ] `@remote-task type=diff` [Remota](https://github.com/user/repo/blob/main/README.md)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("tko.feno.indexer.TestsFinder.find_tests", lambda _folder: False)

    with Console.capture() as capture:
        fix_readme(index_path, tmp_path, verbose=True)

    assert "não possui testes" in capture.getvalue()


def test_fix_readme_normalizes_read_fields_and_eval(tmp_path: Path) -> None:
    from tko.feno.indexer import fix_readme

    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()
    task_dir = base_dir / "reading"
    task_dir.mkdir()
    (task_dir / "README.md").write_text("# Leitura\n", encoding="utf-8")
    index_path.write_text(
        "- [ ] `@reading gain=4 hard=3 size=2 type=read eval=test` [Leitura](base/reading/README.md)\n",
        encoding="utf-8",
    )

    fix_readme(index_path, base_dir, verbose=False)

    line = next(line for line in index_path.read_text(encoding="utf-8").splitlines() if "@reading" in line)
    assert "type=wiki gain=4 hard=3 size=2" in line
    assert "eval=" not in line


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
        "- [x] `@soma gain=2 hard=1 size=1 type=diff` [Soma](base/soma/README.md)\n"
        "- [x] `@media gain=3 hard=1 size=1 type=diff` [Media](base/media/README.md)\n"
        "- [ ] `@desafio gain=5 hard=3 size=2 type=diff` [Desafio](base/desafio/README.md)\n",
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
    line.init_by_line("- [ ] `@task type=wiki` [Título antigo](task/README.md)")
    elements.lines = ["texto", line]
    elements.fix_titles(load_titles=True)

    assert line.tm.title == "Título do arquivo"
