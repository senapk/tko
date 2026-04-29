from tko.util.rtext import RText
from tko.widget.fmt import Fmt

class TestSimple:
    def test_split_1(self):
        values = Fmt.cut_box(6, 6, 10, 10, RText("1234\n56\n789") + RText("1\n23", "r") + RText("456", "g"))
        tokens = Fmt.split_in_tokens(values)
        assert ", ".join([str(x) for x in tokens]) == "6:6:(:1234), 7:6:(:56), 8:6:(:789), 8:9:(r:1), 9:6:(r:23), 9:8:(g:45)"

    def test_split_2(self):
        values = Fmt.cut_box(-2, -1, 10, 10, RText("1234\n56\n789") + RText("1\n23", "r") + RText("456", "g"))
        tokens = Fmt.split_in_tokens(values)
        assert ", ".join([str(x) for x in tokens]) == "0:0:(:89), 0:2:(r:1), 1:0:(r:3), 1:1:(g:456)"
