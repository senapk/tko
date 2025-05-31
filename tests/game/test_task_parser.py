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

    def test_1(self):
        # get path of this file
        task = TaskParser("arquivo.md", "database").parse_line("- [ ] [@label complemente](database/label/r.md)", 0)
        assert task is not None
        assert task.key == "label"
        assert task.folder == "database/label"
        assert task.link == "database/label/r.md"
        assert task.link_type == Task.Types.STATIC_FILE
    
    def test_file_not_found(self):
        # get path of this file
        try:
            _ = TaskParser("arquivo.md", "database").parse_line("- [ ] [@label complemente](database/label/f.md)", 0)
        except Warning as e:
            assert str(e).startswith("Arquivo não encontrado")
            return

    def test_2(self):
        database = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
        task = TaskParser("arquivo.md", database).parse_line("- [ ] `@label `[complemente](outside/label/r.md)", 0)
        assert task is not None
        assert task.key == "label"
        assert task.folder == "database/label"
        assert task.link == "outside/label/r.md"
        assert task.link_type == Task.Types.IMPORT_FILE

    def test_3(self):
        database = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
        task = TaskParser("arquivo.md", database).parse_line("- [ ] #veja_url [complemente](http://url.com)", 0)
        assert task is not None
        assert task.key == "veja_url"
        assert task.folder is None
        assert task.link == "http://url.com"
        assert task.link_type == Task.Types.VISITABLE_URL
        
    def test_4(self):
        database = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
        task = TaskParser("arquivo.md", database).parse_line("- [ ] @banana [complemente](http://url.com/teste.md)", 0)
        assert task is not None
        assert task.key == "banana"
        assert task.folder == "database/banana"
        assert task.link == "http://url.com/teste.md"
        assert task.link_type == Task.Types.REMOTE_FILE
