import os
from pathlib import Path

from tko.game.task_parser import TaskParser
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
        assert task.resource.resource_type == ResourceType.EDIT
    
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
