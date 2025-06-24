from tko.util.text import Text
from tko.play.fmt import Fmt
from tko.play.floating import Floating
from tko.play.input_manager import InputManager
from tko.settings.settings import Settings


class FloatingCalibrate(Floating):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.set_header(" Calibrar teclas direcionais ")
        # self.set_text_ljust()
        self.set_footer(" Use Enter para salvar ou ESC para cancelar ")
        self._index = 0
        self._options: list[int] = [settings.app.get_key_left(),
                                   settings.app.get_key_right(),
                                   settings.app.get_key_up(),
                                   settings.app.get_key_down()]
        self._frame.set_border_color("m")
        self._exit_on_action = True
        self.right_dx = 5 # shortcut space
        self.settings = settings
        self.set_key_content()

    def set_key_content(self):
        def format_value(value: int) -> str:
            if value == 0:
                return "---"
            return str(value)
        self._content = []
        color = "G" if self._index == 0 else ""
        self._content.append(Text().addf(color, "Left  ").addf(color, format_value(self._options[0])))
        color = "G" if self._index == 1 else ""
        self._content.append(Text().addf(color, "Right ").addf(color, format_value(self._options[1])))
        color = "G" if self._index == 2 else ""
        self._content.append(Text().addf(color, "Up    ").addf(color, format_value(self._options[2])))
        color = "G" if self._index == 3 else ""
        self._content.append(Text().addf(color, "Down  ").addf(color, format_value(self._options[3])))

    # @override
    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        key = InputManager.fix_cedilha(Fmt.get_screen(), key)
        
        if key == InputManager.esc:
            self._enable = False
        elif key == ord('\n'):
            self._enable = False
            self.settings.app.set_key_left(self._options[0])
            self.settings.app.set_key_right(self._options[1])
            self.settings.app.set_key_up(self._options[2])
            self.settings.app.set_key_down(self._options[3])
            self.settings.save_settings()
            return -1
        elif key > 128:
            self._options[self._index] = key
            for i in range(len(self._options)):
                if i != self._index and self._options[i] == key:
                    self._options[i] = 0
            self._index += 1
            if self._index >= len(self._options):
                self._index = 0
            self.set_key_content()
        return -1
