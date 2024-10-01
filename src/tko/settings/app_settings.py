from tko.util.consts import DiffMode

class AppSettings:

    def __init__(self):
        self._rootdir = ""
        self._diff_mode = str(DiffMode.SIDE)
        self._lang_default = ""
        self._last_rep = ""
        self._use_images = False
        self._use_borders = False
        self._editor = "code"
        self._timeout = 1

    def to_dict(self):
        return self.__dict__
    
    def from_dict(self, attr_dict):
        for key, value in attr_dict.items():
            if hasattr(self, key) and type(getattr(self, key)) == type(value):
                setattr(self, key, value)
        return self

    def toggle_diff(self):
        if self._diff_mode == DiffMode.SIDE.value:
            self._diff_mode = DiffMode.DOWN.value
        else:
            self._diff_mode = DiffMode.SIDE.value

    def toggle_borders(self):
        self._use_borders = not self._use_borders
    
    def toggle_images(self):
        self._use_images = not self._use_images

    def set_rootdir(self, rootdir: str):
        self._rootdir = rootdir
        return self

    def set_diff_mode(self, diff_mode: DiffMode):
        self._diff_mode = str(diff_mode)
        return self

    def set_side_size_min(self, side_size_min: int):
        self._side_size_min = side_size_min
        return self

    def set_lang_default(self, lang_default: str):
        self._lang_default = lang_default
        return self

    def set_last_rep(self, last_rep: str):
        self._last_rep = last_rep
        return self

    def set_borders(self, borders: bool):
        self._use_borders = borders
        return self

    def set_editor(self, editor: str):
        self._editor = editor
        return self

    def set_timeout(self, timeout: int):
        self._timeout = timeout
        return self

    def get_rootdir(self) -> str:
        return self._rootdir

    def get_diff_mode(self) -> DiffMode:
        if self._diff_mode == DiffMode.SIDE.value:
            return DiffMode.SIDE
        return DiffMode.DOWN

    def get_lang_default(self) -> str:
        return self._lang_default

    def get_last_rep(self) -> str:
        return self._last_rep

    def has_images(self) -> bool:
        return self._use_images

    def has_borders(self) -> bool:
        return self._use_borders

    def get_editor(self) -> str:
        return self._editor

    def get_timeout(self) -> int:
        return self._timeout