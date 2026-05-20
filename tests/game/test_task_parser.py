import os
from pathlib import Path

from tko.game.task_parser import TaskParser
from tko.game.task_config import TaskLoss, TaskEval
from tko.game.task_resource import ResourceType
from tko.repository.git_cache import GitCache

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_database_legacy(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="database")
        task = tp.parse_line("- [ ] [@label complemente](data/label/r.md)", 0)
        assert task is not None
        assert task.basic.key == "label"
        assert task.basic.remote_name == "database"
        assert task.basic.full_key == "database@label"
        assert task.resource.raw_link == "data/label/r.md"
        assert task.resource.remote_dir == Path("/source")
        assert task.resource.relative_path == Path("data/label/r.md")
        assert task.resource.resource_type == ResourceType.TASK
    
    def test_database_poo(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")
        task = tp.parse_line("- [ ] [@label complemente](data/label/r.md)", 0)
        assert task is not None
        assert task.basic.key == "label"
        assert task.basic.remote_name == "poo"
        assert task.basic.full_key == "poo@label"
        assert task.resource.relative_path == Path("data/label/r.md")
        assert task.resource.raw_link == "data/label/r.md"


    def test_STATIC_FILE(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")
        task = tp.parse_line("- [ ] [@label complemente](poo/label/r.md)", 0)
        assert task is not None
        assert task.basic.key == "label"
        assert task.basic.remote_name == "poo"
        assert task.basic.full_key == "poo@label"
        assert task.resource.relative_path == Path("poo/label/r.md")
        assert task.resource.raw_link == "poo/label/r.md"

    def test_file_not_found(self):
        task = (
            TaskParser(index_path=(Path.cwd() / "arquivo.md"), remote_dir_root=Path.cwd(), remote_name="database")
            .parse_line("- [ ] [@label complemente](database/label/f.md)", 0)
        )
        assert task is not None
        task.root_dir = Path.cwd()
        task.git_cache = GitCache(Path.cwd() / ".tko" / "cache_test")
        assert task.path.check_origin_path() is False

    def test_do_task_with_github_blob_url_is_parsed_and_redirected(self):
        tp = TaskParser(
            index_path=Path("/source/arquivo.md"),
            remote_dir_root=Path("/source"),
            remote_name="poo",
            remote_git_url="https://github.com/local/repo",
            editable_source=True,
        )

        task = tp.parse_line(
            "- [ ] [@label :do complemente](https://github.com/user/repo/blob/main/folder/file.md)",
            7,
        )

        assert task is not None
        assert task.resource.resource_type == ResourceType.TASK
        assert task.resource.external_url is None
        assert task.resource.remote_git == "https://github.com/user/repo"
        assert task.resource.remote_dir == Path("/source")
        assert task.resource.relative_path == Path("folder/file.md")
        assert task.resource.editable_source is False

    def test_do_task_with_github_tree_url_is_parsed_and_redirected(self):
        tp = TaskParser(
            index_path=Path("/source/arquivo.md"),
            remote_dir_root=Path("/source"),
            remote_name="poo",
            remote_git_url="https://github.com/local/repo",
            editable_source=True,
        )

        task = tp.parse_line(
            "- [ ] [@label :do complemente](https://github.com/user/repo/tree/main/folder/sub)",
            8,
        )

        assert task is not None
        assert task.resource.resource_type == ResourceType.TASK
        assert task.resource.external_url is None
        assert task.resource.remote_git == "https://github.com/user/repo"
        assert task.resource.remote_dir == Path("/source")
        assert task.resource.relative_path == Path("folder/sub")
        assert task.resource.editable_source is False

    def test_do_task_with_external_non_github_url_becomes_read(self):
        tp = TaskParser(
            index_path=Path("/source/arquivo.md"),
            remote_dir_root=Path("/source"),
            remote_name="poo",
            remote_git_url="https://github.com/local/repo",
            editable_source=True,
        )

        task = tp.parse_line(
            "- [ ] [@label :do complemente](https://example.com/material)",
            9,
        )

        assert task is not None
        assert task.resource.resource_type == ResourceType.READ
        assert task.resource.external_url == "https://example.com/material"
        assert task.resource.editable_source is False

    def test_parse_line_returns_none_for_non_task_line(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")
        assert tp.parse_line("texto comum sem marcador", 1) is None

    def test_parse_line_returns_none_when_key_is_missing(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")
        assert tp.parse_line("- [ ] [titulo sem chave](data/label/r.md)", 2) is None

    def test_read_task_external_url_sets_default_free_and_self(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")
        task = tp.parse_line("- [ ] `@ref :read`[material](https://example.com/material)", 3)

        assert task is not None
        assert task.resource.resource_type == ResourceType.READ
        assert task.resource.external_url == "https://example.com/material"
        assert task.config.loss == TaskLoss.FREE
        assert task.config.test == TaskEval.SELF

    def test_decode_task_types_sets_expected_values(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")
        task = tp.parse_line("- [ ] :15:test:perk:zero [@label title](data/label/r.md)", 0)

        assert task is not None
        assert task.game.xp == 15
        assert task.config.test == TaskEval.TEST
        assert task.config.loss == TaskLoss.ZERO

    def test_redirect_from_readme_keeps_absolute_paths(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")
        absolute = "/tmp/file.md"
        assert tp.redirect_from_readme(absolute) == absolute

    def test_decode_task_types_covers_self_main_side_free_and_part(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")
        task = tp.parse_line("- [ ] :self:free:part [@label title](data/label/r.md)", 0)

        assert task is not None
        # Last tag wins for main/loss in this sequence.
        assert task.config.test == TaskEval.SELF
        assert task.config.loss == TaskLoss.PART

    def test_parse_line_applies_tags_from_title_and_keeps_plain_words(self):
        tp = TaskParser(index_path=Path("/source/arquivo.md"), remote_dir_root=Path("/source"), remote_name="poo")

        task = tp.parse_line("- [ ] [@label :self:free titulo](data/label/r.md)", 12)

        assert task is not None
        assert task.basic.key == "label"
        assert task.basic.title == "titulo"
        assert task.config.test == TaskEval.SELF
        assert task.config.loss == TaskLoss.FREE
