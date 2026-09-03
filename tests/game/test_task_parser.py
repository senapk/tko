from pathlib import Path
from tko.game.task_enums import TaskEval, TaskType
from tko.game.task_parser import TaskParser


def make_parser(external_source: bool = False) -> TaskParser:
    return TaskParser(index_path=Path("/source/arquivo.md"), external_source=external_source)


def test_parse_legacy_link_task() -> None:
    task = make_parser().parse_line("- [ ] `@label type=diff` [complemente](data/label/README.md)", 0)

    assert task is not None
    assert task.basic.key == "label"
    assert task.basic.full_key == "@label"
    assert task.basic.title == "complemente"
    assert task.location.raw_link == "data/label/README.md"
    assert task.location.index_path == Path("/source/arquivo.md")
    assert task.location.line_number == 0
    assert task.location.task_type == TaskType.DIFF
    assert task.location.git_hub_url is None
    assert task.location.external_source is False


def test_parse_github_blob_url_sets_github_structure() -> None:
    task = make_parser(external_source=True).parse_line(
        "- [ ] `@label type=diff` [complemente](https://github.com/user/repo/blob/main/folder/README.md)",
    )

    assert task is not None
    assert task.location.task_type == TaskType.DIFF
    assert task.location.is_task_from_git is True
    assert task.location.materialization.value == "external"
    assert task.location.external_source is True
    assert task.location.git_hub_url is not None
    assert task.location.git_hub_url.repository_url == "https://github.com/user/repo"
    assert task.location.git_hub_url.relative_path == "folder/README.md"


def test_parse_github_tree_url_is_rejected() -> None:
    import pytest
    with pytest.raises(ValueError, match="README.md"):
        make_parser().parse_line(
            "- [ ] `@label type=diff` [complemente](https://github.com/user/repo/tree/main/folder/sub)",
        )


def test_external_non_github_url_is_rejected() -> None:
    import pytest
    with pytest.raises(ValueError, match="local README.md or a GitHub README.md"):
        make_parser().parse_line(
            "- [ ] `@label type=diff` [complemente](https://example.com/material)",
            9,
        )


def test_parse_line_returns_none_for_non_task_line() -> None:
    assert make_parser().parse_line("texto comum sem marcador", 1) is None


def test_parse_line_returns_none_when_key_and_readme_are_missing() -> None:
    assert make_parser().parse_line("- [ ] `type=wiki` [titulo sem chave](data/label/r.md)", 2) is None


def test_parse_local_readme_derives_key_from_repository_path() -> None:
    task = TaskParser(index_path=Path("/source/README.md")).parse_line(
        "- [ ] `type=wiki` [Carro](labs/carro/README.md)",
    )

    assert task is not None
    assert task.basic.key == "labs/carro"


def test_read_task_external_url_is_rejected() -> None:
    import pytest
    with pytest.raises(ValueError):
        make_parser().parse_line("- [ ] `@ref type=read`[material](https://example.com/material)", 3)


def test_read_task_github_url_stays_external_and_uses_self_eval() -> None:
    task = make_parser(external_source=True).parse_line(
        "- [ ] `@ref type=wiki` [material](https://github.com/user/repo/blob/main/README.md)",
    )

    assert task is not None
    assert task.location.task_type == TaskType.READ
    assert task.location.is_read_http_link is True
    assert task.location.git_hub_url is not None
    assert task.location.is_external is True
    assert task.location.external_source is True
    assert task.config.type == TaskType.WIKI


def test_decode_task_types_sets_expected_values() -> None:
    task = make_parser().parse_line("- [ ] :15:test:make:zero [@label title](data/label/README.md)", 0)

    assert task is not None
    assert task.game.gain == 15
    assert task.config.test == TaskEval.TEST
    assert task.location.task_type == TaskType.DIFF


def test_redirect_from_readme_keeps_absolute_paths() -> None:
    absolute = "/tmp/file.md"
    assert make_parser().redirect_from_readme(absolute) == absolute


def test_redirect_from_readme_resolves_relative_paths() -> None:
    assert make_parser().redirect_from_readme("folder/file.md") == "/source/folder/file.md"


def test_decode_task_types_covers_self_and_make_while_ignoring_legacy_loss_tags() -> None:
    task = make_parser().parse_line("- [ ] :self:free:part:make [@label title](data/label/README.md)", 0)

    assert task is not None
    assert task.config.test == TaskEval.SELF
    assert task.location.task_type == TaskType.SELF


def test_parse_line_applies_tags_from_title_and_keeps_plain_words() -> None:
    task = make_parser().parse_line("- [ ] [@label type=self titulo](data/label/README.md)", 12)

    assert task is not None
    assert task.basic.key == "label"
    assert task.basic.title == "titulo"
    assert task.config.test == TaskEval.SELF


def test_parse_line_sets_gain_hard_size_correctly() -> None:
    task = make_parser().parse_line(
        "- [ ] `@calc gain=4 hard=2 size=3 type=self` [Calculadora](calc/README.md)",
        5,
    )

    assert task is not None
    assert task.basic.key == "calc"
    assert task.game.gain == 4
    assert task.game.hard == 2
    assert task.game.size == 3
    assert task.location.task_type == TaskType.SELF
    assert task.config.test == TaskEval.SELF


def test_new_task_types_are_the_single_source_of_evaluation_mode() -> None:
    wiki = make_parser().parse_line("- [ ] `@wiki type=wiki` [Consulta](wiki/README.md)")
    self_task = make_parser().parse_line("- [ ] `@self type=self` [Resumo](self/README.md)")
    diff = make_parser().parse_line("- [ ] `@diff type=diff` [Código](diff/README.md)")
    code = make_parser().parse_line("- [ ] `@code type=code` [Testes](code/README.md)")

    assert wiki is not None and wiki.config.type == TaskType.WIKI
    assert self_task is not None and self_task.config.type == TaskType.SELF
    assert diff is not None and diff.config.type == TaskType.DIFF
    assert code is not None and code.config.type == TaskType.CODE


def test_task_type_is_required() -> None:
    import pytest

    with pytest.raises(ValueError, match="Task type is required"):
        make_parser().parse_line("- [ ] `@missing_type` [Sem tipo](missing/README.md)")


def test_wiki_does_not_accept_separate_evaluation_marker() -> None:
    import pytest

    with pytest.raises(ValueError, match="eval= is obsolete"):
        make_parser().parse_line("- [ ] `@wiki type=wiki eval=self` [Consulta](wiki/README.md)")
