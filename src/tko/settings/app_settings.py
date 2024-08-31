from typing import Any, Dict

class AppSettings:
    def __init__(self):
        self.rootdir = ""
        self.is_ascii = False
        self.is_colored = True
        self.diff_mode = "side"
        self.side_size_min = 80
        self.lang_default = ""
        self.last_rep = ""
        self.borders = False
        self.editor = "code"
        self.timeout = 1

    def to_dict(self):
        return self.__dict__
    
    def from_dict(self, attr_dict):
        for key, value in attr_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def toggle_color(self):
        self.is_colored = not self.is_colored
    
    def toggle_borders(self):
        self.borders = not self.borders
