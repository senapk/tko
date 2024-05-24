# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.settings import SettingsParser


class TestSimple(unittest.TestCase):

    def test_add_one(self):
        print("ping")
        sp = SettingsParser("x.json")
        rfup = sp.settings.reps["fup"]
        rfup.get_file()
        sp.save_settings()
        print(str(sp))


if __name__ == '__main__':
    unittest.main()
