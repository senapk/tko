from tko.util.text import Text
from tko.play.fmt import Fmt

class TestSimple:
    def test_split_1(self):
        values = Fmt.cut_box(6, 6, 10, 10, Text().add("1234\n56\n789").addf("r", "1\n23").addf("g", "456"))
        tokens = Fmt.split_in_tokens(values)
        assert ", ".join([str(x) for x in tokens]) == "6:6:(:1234), 7:6:(:56), 8:6:(:789), 8:9:(r:1), 9:6:(r:23), 9:8:(g:45)"

    def test_split_2(self):
        values = Fmt.cut_box(-2, -1, 10, 10, Text().add("1234\n56\n789").addf("r", "1\n23").addf("g", "456"))
        tokens = Fmt.split_in_tokens(values)
        assert ", ".join([str(x) for x in tokens]) == "0:0:(:89), 0:2:(r:1), 1:0:(r:3), 1:1:(g:456)"
