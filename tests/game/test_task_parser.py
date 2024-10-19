# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.game.task import Task, TaskParser

class TestSimple(unittest.TestCase):
    def test_1(self):
        task = TaskParser.parse_line("- [ ] [@label complemente](r.md)", 0)
        assert task is not None


if __name__ == "__main__":
    unittest.main()
