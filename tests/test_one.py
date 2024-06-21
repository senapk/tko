# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.game import TaskParser, Task


class TestSimple(unittest.TestCase):

    def test_reading_task(self):
        task: Task = TaskParser.parse_line("- [ ] [tarefa um](wiki/tarefa.md)", 0)
        assert task.key == "wiki/tarefa.md"
        assert task.link == "wiki/tarefa.md"
        assert task.grade == 0
        assert task.title == "tarefa um"

    def test_coding_local_task(self):
        task: Task = TaskParser.parse_line("- [ ] [minha @boneca quebrou](base/boneca/Readme.md)", 0)
        assert task.key == "boneca"
        assert task.link == "base/boneca/Readme.md"
        assert task.grade == 0
        assert task.title == "minha @boneca quebrou"


if __name__ == '__main__':
    unittest.main()
