class AppSettings:
    def __init__(self):
        self._rootdir = ""
        self._is_ascii = False
        self._is_colored = True
        self._diff_mode = "side"
        self._side_size_min = 80
        self._lang_default = ""
        self._last_rep = ""
        self._borders = False
        self._editor = "code"
        self._timeout = 1

    def to_dict(self):
        return self.__dict__
    
    def from_dict(self, attr_dict):
        for key, value in attr_dict.items():
            if hasattr(self, key) and type(getattr(self, key)) == type(value):
                setattr(self, key, value)
        return self

    def toggle_color(self):
        self._is_colored = not self._is_colored
    
    def toggle_borders(self):
        self._borders = not self._borders

    def set_rootdir(self, rootdir: str):
        self._rootdir = rootdir
        return self

    def set_ascii(self, is_ascii: bool):
        self._is_ascii = is_ascii
        return self

    def set_colored(self, is_colored: bool):
        self._is_colored = is_colored
        return self

    def set_diff_mode(self, diff_mode: str):
        self._diff_mode = diff_mode
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
        self._borders = borders
        return self

    def set_editor(self, editor: str):
        self._editor = editor
        return self

    def set_timeout(self, timeout: int):
        self._timeout = timeout
        return self

    def get_rootdir(self) -> str:
        return self._rootdir

    def is_ascii(self) -> bool:
        return self._is_ascii

    def is_colored(self) -> bool:
        return self._is_colored

    def get_diff_mode(self) -> str:
        return self._diff_mode

    def get_side_size_min(self) -> int:
        return self._side_size_min

    def get_lang_default(self) -> str:
        return self._lang_default

    def get_last_rep(self) -> str:
        return self._last_rep

    def has_borders(self) -> bool:
        return self._borders

    def get_editor(self) -> str:
        return self._editor

    def get_timeout(self) -> int:
        return self._timeout