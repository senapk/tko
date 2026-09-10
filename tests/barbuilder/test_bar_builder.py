from tko.widget.bar_builder import BarBuilder
from tko.util.rt import RT

class Test:    
    def test_progress_xp_with_zero_reference_is_an_empty_bar(self):
        result = BarBuilder().build_progress_xp(
            obtained=0,
            target100=0,
            available=0,
            reference=0,
            length=8,
        )

        assert result.plain() == " " * 8

    def test_progress_xp_with_non_positive_length_is_empty(self):
        result = BarBuilder().build_progress_xp(
            obtained=0,
            target100=0,
            available=0,
            reference=0,
            length=0,
        )

        assert result.plain() == ""

    def test_convert(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 10, "t", "f")
        assert str(res) == str(RT.parse("[t]{}[][f]{}".format("abcde", "fghij")))
    
    def test_convert2(self):
        res = BarBuilder().build_bar("abcdefghij", 1, 10, "t", "f")
        assert str(res) == str(RT.parse("[t]{}[][f]{}".format("abcdefghij", "")))
    
    def test_convert3(self):
        res = BarBuilder().build_bar("abcdefghij", 0, 10, "t", "f")
        assert str(res) == str(RT.parse("[t]{}[][f]{}".format("", "abcdefghij")))

    def test_convert4(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 12, "t", "f")
        assert str(res) == str(RT.parse("[t]{}[][f]{}".format(" abcde", "fghij ")))

    def test_convert5(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 8, "t", "f")
        assert str(res) == str(RT.parse("[t]{}[][f]{}".format("abcd", "efgh")))

    def test_convert6(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 10, "G", "R")
        assert str(res) == str(RT.parse("[G]{}[][R]{}".format("abcde", "fghij")))

    def test_convert7(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 11, "G", "R")
        assert str(res) == str(RT.parse("[G]{}[][R]{}".format("abcdef", "ghij ")))

    def test_convert8(self):
        res = BarBuilder().build_bar("abcdefghij", 0, 11, "G", "R")
        assert str(res) == str(RT.parse("[R]{}{}".format("abcdefghij ", "")))

    def test_convert9(self):
        res = BarBuilder().build_bar("abcdefghij", 0, 11, "G", "R")
        assert str(res) == str(RT.parse("[R]{}{}".format("abcdefghij ", "")))
