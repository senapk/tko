# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.play.patch_history import PatchHistory
import os
from pathlib import Path

data_expected = r"""{
    "patches": [
        {
            "label": "primeira",
            "content": "@@ -1,5 +1,5 @@\n-H\n+h\n oje \n@@ -23,8 +23,8 @@\n r a \n-D\n+d\n eus\n"
        },
        {
            "label": "segunda",
            "content": "@@ -27,31 +27,4 @@\n Deus\n-%0Aem nos habita seu espirito\n"
        },
        {
            "label": "terceira",
            "content": "@@ -1,8 +1,9 @@\n+H\n oje eh t\n"
        },
        {
            "label": "quarta",
            "content": "oje eh tempo de louvar a Deus\nem nos habita seu espirito"
        }
    ]
}"""

data2_expected = r"""{
    "patches": [
        {
            "label": "primeira",
            "content": "hoje eh tempo de louvar a deus"
        },
        {
            "label": "segunda",
            "content": "Hoje eh tempo de louvar a Deus"
        },
        {
            "label": "terceira",
            "content": "Hoje eh tempo de louvar a Deus\nem nos habita seu espirito"
        },
        {
            "label": "quarta",
            "content": "oje eh tempo de louvar a Deus\nem nos habita seu espirito"
        }
    ]
}"""

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)
        if os.path.exists("data.json"):
            os.remove("data.json")
        if os.path.exists("data2.json"):
            os.remove("data2.json")

    def test_token_creation(self):
        ph = PatchHistory()
        ph.store_version("primeira", "hoje eh tempo de louvar a deus")
        ph.store_version("segunda", "Hoje eh tempo de louvar a Deus")
        ph.store_version("terceira", "Hoje eh tempo de louvar a Deus\nem nos habita seu espirito")
        ph.store_version("quarta", "oje eh tempo de louvar a Deus\nem nos habita seu espirito")

        ph.set_json_file("data.json")
        ph.save_json()

        with open("data.json", "r") as f:
            assert f.read() == data_expected

        ph2 = PatchHistory()
        ph2.set_json_file("data.json")
        ph2.load_json()
        restored = ph2.restore_all()
        ph3 = PatchHistory()
        ph3.patches = restored
        ph3.set_json_file("data2.json")
        ph3.save_json()

        with open("data2.json", "r") as f:
            assert f.read() == data2_expected


if __name__ == "__main__":
    unittest.main()
