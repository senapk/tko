from pathlib import Path

import pytest

from tko.game.task_enums import EvalMode
from tko.game.task_parser import TaskParser


def make_parser(external_source: bool = False) -> TaskParser:
    return TaskParser(index_path=Path("/source/arquivo.md"), external_source=external_source)


def test_parse_diff_task() -> None:
    task = make_parser().parse_line("- [ ] `@label eval=diff` [complemente](data/label/README.md)", 0)
    assert task is not None
    assert task.basic.key == "label"
    assert task.location.eval == EvalMode.DIFF
    assert task.config.eval == EvalMode.DIFF


def test_parse_github_blob_url_sets_github_structure() -> None:
    task = make_parser(external_source=True).parse_line(
        "- [ ] `@label eval=diff` [complemente](https://github.com/user/repo/blob/main/folder/README.md)"
    )
    assert task is not None
    assert task.location.eval == EvalMode.DIFF
    assert task.location.is_task_from_git
    assert task.location.is_external


def test_parse_local_none_task_derives_key() -> None:
    task = TaskParser(index_path=Path("/source/README.md")).parse_line(
        "- [ ] `eval=none` [Carro](labs/carro/README.md)"
    )
    assert task is not None
    assert task.basic.key == "labs/carro"
    assert task.location.is_non_evaluated


def test_parse_line_applies_tags_from_title_and_keeps_plain_words() -> None:
    task = make_parser().parse_line("- [ ] [@label eval=self titulo](data/label/README.md)", 12)
    assert task is not None
    assert task.basic.title == "titulo"
    assert task.config.eval == EvalMode.SELF


def test_parse_line_sets_gain_cost_size_and_xp() -> None:
    task = make_parser().parse_line(
        "- [ ] `@calc gain=2 cost=1 size=2 eval=self` [Calculadora](calc/README.md)", 5
    )
    assert task is not None
    assert task.game.cost == 1
    assert task.xp == 2.0


def test_gcs_expands_indicators_for_xp_calculation() -> None:
    task = make_parser().parse_line(
        "- [ ] `@calc gcs=312 eval=self` [Calculadora](calc/README.md)", 5
    )
    assert task is not None
    assert (task.game.gain, task.game.cost, task.game.size) == (3, 1, 2)
    assert task.xp == 2.5


def test_maximum_indicator_values_produce_eighteen_xp() -> None:
    task = make_parser().parse_line(
        "- [ ] `@max gain=3 cost=6 size=3 eval=diff` [Máxima](max/README.md)"
    )
    assert task is not None
    assert task.xp == 18.0


def test_none_has_no_xp_and_reference_is_preserved() -> None:
    reference = make_parser().parse_line(
        "- [x] `@ref gain=4 cost=2 size=3 eval=diff` [Referência](ref/README.md)"
    )
    material = make_parser().parse_line(
        "- [ ] `@material gain=99 cost=4 size=9 eval=none` [Material](wiki/README.md)"
    )
    assert reference is not None and reference.is_reference and reference.xp == 6.0
    assert material is not None and material.xp == 0.0


@pytest.mark.parametrize("legacy", ["type=wiki", "hard=2", "eval=test", ":make"])
def test_parser_rejects_removed_syntax(legacy: str) -> None:
    with pytest.raises(ValueError):
        make_parser().parse_line(f"- [ ] `@task {legacy}` [Titulo](task/README.md)")


def test_parse_github_tree_url_is_rejected() -> None:
    with pytest.raises(ValueError, match="README.md"):
        make_parser().parse_line(
            "- [ ] `@label eval=diff` [complemente](https://github.com/user/repo/tree/main/folder/sub)"
        )
