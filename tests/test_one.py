# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.game.task import TaskParser, Task # type: ignore


class TestSimple(unittest.TestCase):

    def test_local_task(self):
        task: Task = TaskParser("arquivo.md").parse_line("- [ ] [tarefa um](wiki/tarefa.md)")
        assert task.key == "wiki/tarefa.md"
        assert task.get_download_link() == "wiki/tarefa.md"
        assert task.get_visitable_url() == ""
        assert task.title == "tarefa um"

    def test_remote_task(self):
        task: Task = TaskParser("arquivo.md").parse_line("- [ ] @tarefa [faz tal coisa](https://wiki/tarefa.md)")
        assert task.key == "tarefa"
        assert task.get_download_link() == "https://wiki/tarefa.md"
        assert task.get_visitable_url() == "https://wiki/tarefa.md"
        assert task.title == "@tarefa faz tal coisa"

    def test_coding_local_task(self):
        task: Task = TaskParser("arquivo.md").parse_line("- [ ] [minha !boneca quebrou](base/boneca/Readme.md)", 0)
        assert task.key == "boneca"
        assert task.get_download_link() == ""
        assert task.get_visitable_url() == ""
        assert task.title == "minha !boneca quebrou"


if __name__ == '__main__':
    unittest.main()
