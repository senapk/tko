from tko.util.rtext import RText
from tko.play.floating import Floating, FloatingABC
from tko.config.settings import Settings
import tko.config.app_settings as app

class FloatingCalibrate(FloatingABC):
    def __init__(self, settings: Settings):
        self.floating = Floating()
        self.settings = settings
        self.floating.set_header(" Calibrar teclas direcionais ")
        # self.set_text_ljust()
        self.floating.set_footer_text(RText.parse(" Use [y]Enter[.] para salvar, [y]q[.] para cancelar e [y]r[.] para reiniciar. "))
        self._index = 0
        self._options = [settings.app.get_key(app.AppKeys.LEFT),
                         settings.app.get_key(app.AppKeys.RIGHT),
                         settings.app.get_key(app.AppKeys.UP),
                         settings.app.get_key(app.AppKeys.DOWN),
                         settings.app.get_key(app.AppKeys.ESC),
                         settings.app.get_key(app.AppKeys.PG_UP),
                         settings.app.get_key(app.AppKeys.PG_DOWN),
                         settings.app.get_key(app.AppKeys.BACKSPACE)]
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
        content.append(RText("Left      ", color) + RText(format_value(self._options[0]), color))
        color = "G" if self._index == 1 else ""
        content.append(RText("Right     ", color) + RText(format_value(self._options[1]), color))
        color = "G" if self._index == 2 else ""
        content.append(RText("Up        ", color) + RText(format_value(self._options[2]), color))
        color = "G" if self._index == 3 else ""
        content.append(RText("Down      ", color) + RText(format_value(self._options[3]), color))
        color = "G" if self._index == 4 else ""
        content.append(RText("Esc       ", color) + RText(format_value(self._options[4]), color))
        color = "G" if self._index == 5 else ""
        content.append(RText("PageUp    ", color) + RText(format_value(self._options[5]), color))
        color = "G" if self._index == 6 else ""
        content.append(RText("PageDown  ", color) + RText(format_value(self._options[6]), color))
        color = "G" if self._index == 7 else ""
        content.append(RText("Backspace ", color) + RText(format_value(self._options[7]), color))

    def process_input(self, key: int) -> int:
        # self.draw()
        
        if key == ord('\n'):
            self.floating.enable = False
            self.settings.app.set_key(app.AppKeys.LEFT, self._options[0])
            self.settings.app.set_key(app.AppKeys.RIGHT, self._options[1])
            self.settings.app.set_key(app.AppKeys.UP, self._options[2])
            self.settings.app.set_key(app.AppKeys.DOWN, self._options[3])
            self.settings.app.set_key(app.AppKeys.ESC, self._options[4])
            self.settings.app.set_key(app.AppKeys.PG_UP, self._options[5])
            self.settings.app.set_key(app.AppKeys.PG_DOWN, self._options[6])
            self.settings.app.set_key(app.AppKeys.BACKSPACE, self._options[7])
            self.settings.save_settings()
            return -1
        elif key == ord('q'):
            self.floating.enable = False
            return -1
        elif key == ord('r'):
            self._index = 0
            self.set_key_content()
        elif not (ord('a') <= key <= ord('z') or ord('A') <= key <= ord('Z')) or ord('0') <= key <= ord('9'):
            self._options[self._index] = key
            for i in range(len(self._options)):
                if i != self._index and self._options[i] == key:
                    self._options[i] = 0
            self._index += 1
            if self._index >= len(self._options):
                self._index = 0
            self.set_key_content()
        return -1
