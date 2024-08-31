import unittest
from tko.play.style import Style
from tko.settings.settings import Settings

class Test:    
    def test_convert(self):
        res = Style.build_bar("abcdefghij", 0.5, 10, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghij"
        assert fmt == "tttttfffff"
    
    def test_convert2(self):
        res = Style.build_bar("abcdefghij", 1, 10, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghij"
        assert fmt == "tttttttttt"
    
    def test_convert3(self):
        res = Style.build_bar("abcdefghij", 0, 10, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghij"
        assert fmt == "ffffffffff"

    def test_convert4(self):
        res = Style.build_bar("abcdefghij", 0.5, 12, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == " abcdefghij "
        assert fmt == "ttttttffffff"

    def test_convert5(self):
        res = Style.build_bar("abcdefghij", 0.5, 8, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefgh"
        assert fmt == "ttttffff"

    def test_convert6(self):
        Settings().app.set_nerdfonts(True)
        res = Style.build_bar("abcdefghij", 0.5, 10, "G", "R", round=True)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefgh"
        assert fmt == "gGGGGRRRRr"

    def test_convert7(self):
        Settings().app.set_nerdfonts(True)
        res = Style.build_bar("abcdefghij", 0.5, 11, "G", "R", round=True)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghi"
        assert fmt == "gGGGGRRRRRr"

    def test_convert8(self):
        Settings().app.set_nerdfonts(True)
        res = Style.build_bar("abcdefghij", 0, 11, "G", "R", round=True)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghi"
        assert fmt == "rRRRRRRRRRr"

if __name__ == '__main__':
    unittest.main()
