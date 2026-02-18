from tko.util.text import Text
from tko.play.floating import Floating, FloatingABC
from tko.settings.settings import Settings


class FloatingCalibrate(FloatingABC):
    def __init__(self, settings: Settings):
        self.floating = Floating()
        self.settings = settings
        self.floating.set_header(" Calibrar teclas direcionais ")
        # self.set_text_ljust()
        self.floating.set_footer(" Use Enter para salvar, mas só quando tiver certeza de que as teclas estão corretas ")
        self._index = 0
        self._options: list[int] = [settings.app.get_key_left(),
                                   settings.app.get_key_right(),
                                   settings.app.get_key_up(),
                                   settings.app.get_key_down(), 
                                   settings.app.get_key_esc(),
                                   settings.app.get_key_pg_up(),
                                   settings.app.get_key_pg_down(), 
                                   settings.app.get_key_backspace()]
        self.floating.frame.set_border_color("m")
        self._exit_on_action = True
        self.right_dx = 5 # shortcut space
        self.settings = settings
        self.set_key_content()

    def draw(self):
        self.floating.draw()

    def is_enable(self) -> bool:
        return self.floating.is_enable()

    def set_key_content(self):
        def format_value(value: int) -> str:
            if value == 0:
                return "---"
            return f"{value:>3}"

        content = self.floating.content
        content.clear()
        color = "G" if self._index == 0 else ""
        content.append(Text().addf(color, "Left      ").addf(color, format_value(self._options[0])))
        color = "G" if self._index == 1 else ""
        content.append(Text().addf(color, "Right     ").addf(color, format_value(self._options[1])))
        color = "G" if self._index == 2 else ""
        content.append(Text().addf(color, "Up        ").addf(color, format_value(self._options[2])))
        color = "G" if self._index == 3 else ""
        content.append(Text().addf(color, "Down      ").addf(color, format_value(self._options[3])))
        color = "G" if self._index == 4 else ""
        content.append(Text().addf(color, "Esc       ").addf(color, format_value(self._options[4])))
        color = "G" if self._index == 5 else ""
        content.append(Text().addf(color, "PageUp    ").addf(color, format_value(self._options[5])))
        color = "G" if self._index == 6 else ""
        content.append(Text().addf(color, "PageDown  ").addf(color, format_value(self._options[6])))
        color = "G" if self._index == 7 else ""
        content.append(Text().addf(color, "Backspace ").addf(color, format_value(self._options[7])))

    def process_input(self, key: int) -> int:
        # self.draw()
        
        if key == ord('\n'):
            self.floating.enable = False
            self.settings.app.set_key_left(self._options[0])
            self.settings.app.set_key_right(self._options[1])
            self.settings.app.set_key_up(self._options[2])
            self.settings.app.set_key_down(self._options[3])
            self.settings.app.set_key_esc(self._options[4])
            self.settings.app.set_key_pg_up(self._options[5])
            self.settings.app.set_key_pg_down(self._options[6])
            self.settings.app.set_key_backspace(self._options[7])
            self.settings.save_settings()
            return -1
        else:
            self._options[self._index] = key
            for i in range(len(self._options)):
                if i != self._index and self._options[i] == key:
                    self._options[i] = 0
            self._index += 1
            if self._index >= len(self._options):
                self._index = 0
            self.set_key_content()
        return -1
