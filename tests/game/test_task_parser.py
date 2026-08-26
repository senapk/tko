from pathlib import Path
from tko.game.task_enums import TaskEval, TaskType
from tko.game.task_parser import TaskParser


def make_parser(remote_import: bool = False) -> TaskParser:
    return TaskParser(index_path=Path("/source/arquivo.md"), remote_import=remote_import)


def test_parse_legacy_link_task() -> None:
    task = make_parser().parse_line("- [ ] [@label complemente](data/label/r.md)", 0)

    assert task is not None
    assert task.basic.key == "label"
    assert task.basic.full_key == "@label"
    assert task.basic.title == "complemente"
    assert task.location.raw_link == "data/label/r.md"
    assert task.location.index_path == Path("/source/arquivo.md")
    assert task.location.line_number == 0
    assert task.location.task_type == TaskType.MAKE
    assert task.location.git_hub_url is None
    assert task.location.remote_import is False


def test_parse_github_blob_url_sets_github_structure() -> None:
    task = make_parser(remote_import=True).parse_line(
        "- [ ] `@label type=make` [complemente](https://github.com/user/repo/blob/main/folder/file.md)",
    )

    assert task is not None
    assert task.location.task_type == TaskType.MAKE
    assert task.location.is_task_from_git is True
    assert task.location.is_import_type is True
    assert task.location.remote_import is True
    assert task.location.git_hub_url is not None
    assert task.location.git_hub_url.repository_url == "https://github.com/user/repo"
    assert task.location.git_hub_url.relative_path == "folder/file.md"


def test_parse_github_tree_url_sets_github_structure() -> None:
    task = make_parser().parse_line(
        "- [ ] `@label type=make` [complemente](https://github.com/user/repo/tree/main/folder/sub)",
    )

    assert task is not None
    assert task.location.task_type == TaskType.MAKE
    assert task.location.is_task_from_git is True
    assert task.location.git_hub_url is not None
    assert task.location.git_hub_url.repository_url == "https://github.com/user/repo"
    assert task.location.git_hub_url.relative_path == "folder/sub"


def test_external_non_github_url_is_http_link_without_github_structure() -> None:
    task = make_parser().parse_line(
        "- [ ] `@label type=make` [complemente](https://example.com/material)",
        9,
    )

    assert task is not None
    assert task.location.task_type == TaskType.MAKE
    assert task.location.raw_link == "https://example.com/material"
    assert task.location.is_http_link is True
    assert task.location.git_hub_url is None


def test_parse_line_returns_none_for_non_task_line() -> None:
    assert make_parser().parse_line("texto comum sem marcador", 1) is None


def test_parse_line_returns_none_when_key_is_missing() -> None:
    assert make_parser().parse_line("- [ ] [titulo sem chave](data/label/r.md)", 2) is None


def test_read_task_external_url_sets_default_self_eval() -> None:
    task = make_parser().parse_line("- [ ] `@ref type=read`[material](https://example.com/material)", 3)

    assert task is not None
    assert task.location.task_type == TaskType.READ
    assert task.location.is_read_http_link is True
    assert task.config.test == TaskEval.SELF


def test_decode_task_types_sets_expected_values() -> None:
    task = make_parser().parse_line("- [ ] :15:test:make:zero [@label title](data/label/r.md)", 0)

    assert task is not None
    assert task.game.gain == 15
    assert task.config.test == TaskEval.TEST
    assert task.location.task_type == TaskType.MAKE


def test_redirect_from_readme_keeps_absolute_paths() -> None:
    absolute = "/tmp/file.md"
    assert make_parser().redirect_from_readme(absolute) == absolute


def test_redirect_from_readme_resolves_relative_paths() -> None:
    assert make_parser().redirect_from_readme("folder/file.md") == "/source/folder/file.md"


def test_decode_task_types_covers_self_and_make_while_ignoring_legacy_loss_tags() -> None:
    task = make_parser().parse_line("- [ ] :self:free:part:make [@label title](data/label/r.md)", 0)

    assert task is not None
    assert task.config.test == TaskEval.SELF
    assert task.location.task_type == TaskType.MAKE


def test_parse_line_applies_tags_from_title_and_keeps_plain_words() -> None:
    task = make_parser().parse_line("- [ ] [@label eval=self loss=free titulo](data/label/r.md)", 12)

    assert task is not None
    assert task.basic.key == "label"
    assert task.basic.title == "titulo"
    assert task.config.test == TaskEval.SELF
