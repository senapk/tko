from tko.widget.bar_builder import BarBuilder
from tko.util.rtext import RText

class Test:    
    def test_convert(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 10, "t", "f")
        assert str(res) == str(RText.format("{t}{f}", "abcde", "fghij"))
    
    def test_convert2(self):
        res = BarBuilder().build_bar("abcdefghij", 1, 10, "t", "f")
        assert str(res) == str(RText.format("{t}{f}", "abcdefghij", ""))
    
    def test_convert3(self):
        res = BarBuilder().build_bar("abcdefghij", 0, 10, "t", "f")
        assert str(res) == str(RText.format("{t}{f}", "", "abcdefghij"))

    def test_convert4(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 12, "t", "f")
        assert str(res) == str(RText.format("{t}{f}", " abcde", "fghij "))

    def test_convert5(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 8, "t", "f")
        assert str(res) == str(RText.format("{t}{f}", "abcd", "efgh"))

    def test_convert6(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 10, "G", "R")
        assert str(res) == str(RText.format("{G}{R}", "abcde", "fghij"))

    def test_convert7(self):
        res = BarBuilder().build_bar("abcdefghij", 0.5, 11, "G", "R")
        assert str(res) == str(RText.format("{G}{R}", "abcdef", "ghij "))

    def test_convert8(self):
        res = BarBuilder().build_bar("abcdefghij", 0, 11, "G", "R")
        assert str(res) == str(RText.format("{R}", "abcdefghij "))
    
    def test_convert9(self):
        res = BarBuilder().build_bar("abcdefghij", 0, 11, "G", "R")
        assert str(res) == str(RText.format("{R}", "abcdefghij "))
