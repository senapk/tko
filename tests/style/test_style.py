from tko.play.border import Border
from tko.settings.app_settings import AppSettings
from tko.util.text import Text

class Test:    
    def test_convert(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 0.5, 10, "t", "f", round=False)
        assert str(res) == str(Text.format("{t}{f}", "abcde", "fghij"))
    
    def test_convert2(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 1, 10, "t", "f", round=False)
        assert str(res) == str(Text.format("{t}{f}", "abcdefghij", ""))
    
    def test_convert3(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 0, 10, "t", "f", round=False)
        assert str(res) == str(Text.format("{t}{f}", "", "abcdefghij"))

    def test_convert4(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 0.5, 12, "t", "f", round=False)
        assert str(res) == str(Text.format("{t}{f}", " abcde", "fghij "))

    def test_convert5(self):
        app = AppSettings()
        res = Border(app).build_bar("abcdefghij", 0.5, 8, "t", "f", round=False)
        assert str(res) == str(Text.format("{t}{f}", "abcd", "efgh"))

    def test_convert6(self):
        app = AppSettings()
        app.use_borders = True
        res = Border(app).build_bar("abcdefghij", 0.5, 10, "G", "R", round=True)
        assert str(res) == str(Text.format("{g}{G}{R}{r}", "", "abcd", "efgh", ""))

    def test_convert7(self):
        app = AppSettings()
        app.use_borders = True
        res = Border(app).build_bar("abcdefghij", 0.5, 11, "G", "R", round=True)
        assert str(res) == str(Text.format("{g}{G}{R}{r}", "", "abcd", "efghi", ""))

    def test_convert8(self):
        app = AppSettings()
        app.use_borders = True
        res = Border(app).build_bar("abcdefghij", 0, 11, "G", "R", round=True)
        assert str(res) == str(Text.format("{r}{R}{r}", "", "abcdefghi", ""))
    
    def test_convert9(self):
        app = AppSettings()
        app.use_borders = False
        res = Border(app).build_bar("abcdefghij", 0, 11, "G", "R", round=True)
        assert str(res) == str(Text.format("{R}", " abcdefghi "))
