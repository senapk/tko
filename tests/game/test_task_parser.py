# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import os
from pathlib import Path

from tko.game.task_parser import TaskParser
from tko.game.task import Task

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_database_legacy(self):
        # get path of this file
        tp = TaskParser(index_path="/source/arquivo.md", database="database", rep_folder_path="/rep")
        task = tp.parse_line("- [ ] [@label complemente](data/label/r.md)", 0).get_task()
        assert task is not None
        assert task.get_only_key() == "label"
        assert task.get_database() == "database"
        assert task.get_db_key() == "label" # database is hided by legacy compatibility
        assert task.get_folder_try() == "/rep/database/label"
        assert task.link == "/source/data/label/r.md"
        assert task.link_type == Task.Types.IMPORT_FILE
    
    def test_database_poo(self):
        # get path of this file
        tp = TaskParser(index_path="/source/arquivo.md", database="poo", rep_folder_path="/rep")
        task = tp.parse_line("- [ ] [@label complemente](data/label/r.md)", 0).get_task()
        assert task is not None
        assert task.get_only_key() == "label"
        assert task.get_database() == "poo"
        assert task.get_db_key() == "poo@label" # database is hided by legacy compatibility
        assert task.get_folder_try() == "/rep/poo/label"
        assert task.link == "/source/data/label/r.md"
        assert task.link_type == Task.Types.IMPORT_FILE

    def test_STATIC_FILE(self):
        # get path of this file
        tp = TaskParser(index_path="/source/arquivo.md", database="poo", rep_folder_path="/source")
        task = tp.parse_line("- [ ] [@label complemente](poo/label/r.md)", 0).get_task()
        assert task is not None
        assert task.get_only_key() == "label"
        assert task.get_database() == "poo"
        assert task.get_db_key() == "poo@label" # database is hided by legacy compatibility
        assert task.get_folder_try() == "/source/poo/label"
        assert task.link == "/source/poo/label/r.md"
        assert task.link_type == Task.Types.STATIC_FILE

    def test_file_not_found(self):
        # get path of this file
        try:
            (TaskParser("arquivo.md", "database", "fup")
                .parse_line("- [ ] [@label complemente](database/label/f.md)", 0)
                .check_path_try())
        except Warning as _:
            assert True
            return

    def test_2(self):
        task = (TaskParser("/home/arquivo.md", "fup", "/home/rep")
                    .parse_line("- [ ] `@mykey `[complemente](/outside/label/r.md)", 0)
                    .get_task())
        assert task is not None
        assert task.get_only_key() == "mykey"
        assert task.get_db_key() == "fup@mykey"
        assert task.get_folder_try() == "/home/rep/fup/mykey"
        assert task.link == "/outside/label/r.md"
        assert task.link_type == Task.Types.IMPORT_FILE
        
    def test_remote(self):
        task = TaskParser("/home/arquivo.md", "fup", "/rep").parse_line("- [ ] @banana [complemente](http://url.com/teste.md)", 0).get_task()
        assert task is not None
        assert task.get_folder_try() == "/rep/fup/banana"
        assert task.link == "http://url.com/teste.md"
        assert task.link_type == Task.Types.REMOTE_FILE
