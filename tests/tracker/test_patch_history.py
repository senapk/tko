from tko.play.patch_history import PatchHistory
import os
from pathlib import Path


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
        ph.store_version("quinta", "oje eh tempo de louvar a Deus\numa linha no meio\nem nos habita seu espirito")

        ph.set_json_file("data.json")
        ph.save_json()

        with open("expected1.json", "r") as f:
            data_expected = f.read()

        with open("data.json", "r") as f:
            assert f.read() == data_expected

        ph2 = PatchHistory()
        ph2.set_json_file("data.json")
        ph2.load_json()
        restored = ph2.restore_all()

        with open("data2.txt", "w") as f:
            for info in restored:
                f.write(f"# {info.label}\n{info.content}\n")


        with open("expected2.txt", "r") as f:
            with open("data2.txt", "r") as f2:
                assert f.read() == f2.read()
