from tko.util.consts import DiffMode
from tko.util.text import Text

class AppSettings:

    def __init__(self):
        self.diff_mode = DiffMode.SIDE.value
        self.show_hidden = False
        self.use_images = True
        self.use_borders = False
        self.editor = "code"
        self.timeout = 2

    def to_dict(self):
        return self.__dict__
    
    def from_dict(self, attr_dict):
        for key, value in attr_dict.items():
            if hasattr(self, key) and type(getattr(self, key)) == type(value):
                setattr(self, key, value)
        return self

    def toggle_diff(self):
        if self.diff_mode == DiffMode.SIDE.value:
            self.diff_mode = DiffMode.DOWN.value
        else:
            self.diff_mode = DiffMode.SIDE.value

    def toggle_borders(self):
        self.use_borders = not self.use_borders
    
    def toggle_images(self):
        self.use_images = not self.use_images
    
    def toggle_hidden(self):
        self.show_hidden = not self.show_hidden

    def set_diff_mode(self, diff_mode: DiffMode):
        self.diff_mode = diff_mode.value
        return self

    def set_show_hidden(self, show_hidden: bool):
        self.show_hidden = show_hidden
        return self

    def set_use_borders(self, borders: bool):
        self.use_borders = borders
        return self
    
    def set_use_images(self, images: bool):
        self.use_images = images
        return self

    def set_editor(self, editor: str):
        self.editor = editor
        return self

    def set_timeout(self, timeout: int):
        self.timeout = timeout
        return self

    def get_diff_mode(self) -> DiffMode:
        if self.diff_mode == DiffMode.SIDE.value:
            return DiffMode.SIDE
        return DiffMode.DOWN

    # def get_lang_default(self) -> str:
    #     return self._lang_default

    # def get_last_rep(self) -> str:
    #     return self._last_rep

    def get_show_hidden(self) -> bool:
        return self.show_hidden

    def get_use_images(self) -> bool:
        return self.use_images

    def get_use_borders(self) -> bool:
        return self.use_borders

    def get_editor(self) -> str:
        return self.editor

    def get_timeout(self) -> int:
        return self.timeout

    def __str__(self):
        output: list[str] = []
        output.append(str(Text.format("{g}", "Configurações globais:")))
        output.append("- Diff    : {}".format(str(self.get_diff_mode().value)))
        output.append("- Editor  : {}".format(self.get_editor()))
        output.append("- Bordas  : {}".format(self.get_use_borders()))
        output.append("- Images  : {}".format(self.get_use_images()))
        output.append("- Timeout : {}".format(self.get_timeout()))
        return "\n".join(output)