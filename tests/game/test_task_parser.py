from pathlib import Path

import pytest

from tko.game.source_xp_config import SourceXpConfig, XpExpressionError
from tko.game.task_parser import TaskParser


INDEX = Path("/source/README.md")


def source_config(variables: str, formula: str) -> SourceXpConfig:
    return SourceXpConfig.from_markdown(
        f"---\nvar: [{variables}]\nxp: {formula!r}\n---\n", "course", INDEX
    )


def parse(line: str, variables: str = "value", formula: str = "value"):
    return TaskParser(INDEX, xp_config=source_config(variables, formula)).parse_line(line, 7)


def test_single_variable_is_stored_as_xp_only() -> None:
    task = parse("- [ ] `@one value=3 eval=self` [One](one/README.md)")
    assert task is not None and task.xp == 3.0 and task.game.xp == 3.0
    assert not hasattr(task.game, "gain")
    assert not hasattr(task.game, "cost")
    assert not hasattr(task.game, "size")
    assert not hasattr(task, "variables")


@pytest.mark.parametrize(
    ("formula", "fields", "expected"),
    [
        ("value + depth", "value=3 depth=2", 5.0),
        ("value * depth", "value=3 depth=2", 6.0),
        ("(value + depth) / 2", "value=3 depth=2", 2.5),
        ("value ** depth", "value=3 depth=2", 9.0),
        ("(value * depth * scope) ** (1 / 3)", "value=8 depth=1 scope=1", 2.0),
    ],
)
def test_supported_formulas(formula: str, fields: str, expected: float) -> None:
    variables = "value, depth, scope" if "scope" in formula else "value, depth"
    task = parse(f"- [ ] `@task {fields} eval=diff` [Title](task/README.md)", variables, formula)
    assert task is not None and task.xp == expected


def test_none_keeps_zero_xp_without_variables() -> None:
    task = parse("- [ ] `@reading eval=none` [Reading](reading/README.md)")
    assert task is not None and task.xp == 0.0


def test_none_ignores_legacy_or_source_specific_annotations() -> None:
    task = parse("- [ ] `@reading gain=99 eval=none` [Reading](reading/README.md)")
    assert task is not None and task.xp == 0.0


def test_missing_declared_variable_has_task_context() -> None:
    with pytest.raises(XpExpressionError, match=r"course:.+task @task: missing variable\(s\): depth"):
        parse("- [ ] `@task value=3 eval=self` [Title](task/README.md)", "value, depth", "value + depth")


def test_unconfigured_source_assigns_zero_xp() -> None:
    task = TaskParser(INDEX).parse_line("- [ ] `@legacy gain=3 eval=diff` [Legacy](legacy/README.md)", 7)
    assert task is not None and task.xp == 0.0


@pytest.mark.parametrize(
    "formula, message",
    [
        ("value +", "invalid XP formula"),
        ("value + missing", "undeclared variable"),
        ("__import__('os').system('id')", "unsupported syntax"),
    ],
)
def test_formula_errors_are_rejected_without_execution(formula: str, message: str) -> None:
    with pytest.raises(XpExpressionError, match=message):
        source_config("value", formula)
