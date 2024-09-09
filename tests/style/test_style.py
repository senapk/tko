import unittest
from tko.play.border import Border
from tko.settings.app_settings import AppSettings

class Test:    
    def test_convert(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 0.5, 10, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghij"
        assert fmt == "tttttfffff"
    
    def test_convert2(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 1, 10, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghij"
        assert fmt == "tttttttttt"
    
    def test_convert3(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 0, 10, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghij"
        assert fmt == "ffffffffff"

    def test_convert4(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 0.5, 12, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == " abcdefghij "
        assert fmt == "ttttttffffff"

    def test_convert5(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 0.5, 8, "t", "f", round=False)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefgh"
        assert fmt == "ttttffff"

    def test_convert6(self):
        app = AppSettings()
        app._use_borders = True
        res = Border(app).build_bar("abcdefghij", 0.5, 10, "G", "R", round=True)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefgh"
        assert fmt == "gGGGGRRRRr"

    def test_convert7(self):
        app = AppSettings()
        app._use_borders = True
        res = Border(app).build_bar("abcdefghij", 0.5, 11, "G", "R", round=True)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghi"
        assert fmt == "gGGGGRRRRRr"

    def test_convert8(self):
        app = AppSettings()
        app._use_borders = True
        res = Border(app).build_bar("abcdefghij", 0, 11, "G", "R", round=True)
        val, fmt = res.resume_val_fmt()
        assert val == "abcdefghi"
        assert fmt == "rRRRRRRRRRr"
    
    def test_convert9(self):
        app = AppSettings()
        app._use_borders = False
        res = Border(app).build_bar("abcdefghij", 0, 11, "G", "R", round=True)
        val, fmt = res.resume_val_fmt()
        assert val == " abcdefghi "
        assert fmt == "RRRRRRRRRRR"

if __name__ == '__main__':
    unittest.main()
