# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import os
from pathlib import Path

from tko.game.task_parser import TaskParser

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_database_legacy(self):
        # get path of this file
        tp = TaskParser(index_path=Path("/source/arquivo.md"), source_alias="database")
        task = tp.parse_line("- [ ] [@label complemente](data/label/r.md)", 0).get_task()
        assert task is not None
        task.set_origin_folder(Path("/ping/database/label"))
        task.set_workspace_folder(Path("/rep/database/label"))
        assert task.get_key() == "label"
        assert task.get_remote_name() == "database"
        assert task.get_full_key() == "label" # database is hided by legacy compatibility
        folder = task.get_workspace_folder()
        assert folder is not None
        assert str(folder.resolve()) == "/rep/database/label"
        assert task.target == "data/label/r.md"
    
    def test_database_poo(self):
        # get path of this file
        tp = TaskParser(index_path=Path("/source/arquivo.md"), source_alias="poo")
        task = tp.parse_line("- [ ] [@label complemente](data/label/r.md)", 0).get_task()
        assert task is not None
        assert task.get_key() == "label"
        assert task.get_remote_name() == "poo"
        assert task.get_full_key() == "poo@label" # database is hided by legacy compatibility
        assert str(task.get_workspace_folder()) == "/source/data/label"
        assert task.target == "data/label/r.md"


    def test_STATIC_FILE(self):
        # get path of this file
        tp = TaskParser(index_path=Path("/source/arquivo.md"), source_alias="poo")
        task = tp.parse_line("- [ ] [@label complemente](poo/label/r.md)", 0).get_task()
        assert task is not None
        assert task.get_key() == "label"
        assert task.get_remote_name() == "poo"
        assert task.get_full_key() == "poo@label" # database is hided by legacy compatibility
        assert str(task.get_workspace_folder()) == "/source/poo/label"
        assert task.target == "poo/label/r.md"

    def test_file_not_found(self):
        # get path of this file
        try:
            (TaskParser(index_path=Path("arquivo.md"), source_alias="database")
                .parse_line("- [ ] [@label complemente](database/label/f.md)", 0)
                .check_path_try())
        except Warning as _:
            assert True
            return
