from typing import Any, Dict

class AppSettings:
    __rootdir = "rootdir"
    __is_ascii = "ascii"
    __is_color = "color"
    __diffmode = "diffmode"
    __sidesize = "sidesize"
    __langdef = "langdef"
    __lastrep = "lastrep"
    __nerdfonts = "nerdfonts"
    __editor = "editor"
    __timeout = "timeout"

    defaults = {
        __rootdir: "",
        __is_ascii: False,
        __is_color: True,
        __diffmode: "side",
        __sidesize: 80,
        __langdef: "",
        __lastrep: "", 
        __nerdfonts: False,
        __editor: "code",
        __timeout: 1
    }

    def __init__(self):
        self.data: Dict[str, Any] = {}
        for key in AppSettings.defaults:
            self.data[key] = AppSettings.defaults[key]

    def __set(self, key: str, value: Any):
        self.data[key] = value
        return self

    def __get(self, key: str) -> Any:
        if key not in self.defaults:
            raise ValueError(f"Key {key} not found in AppSettings")
        if key not in self.data:
            self.data[key] = AppSettings.defaults[key]
        return self.data[key]


    def get_timeout(self) -> int:
        return self.__get(self.__timeout)
    
    def set_timeout(self, value: int):
        self.__set(self.__timeout, value)
        return self

    def get_editor(self) -> str:
        return self.__get(self.__editor)
    
    def set_editor(self, value: str):
        self.__set(self.__editor, value)
        return self

    def get_last_rep(self) -> str:
        return self.__get(self.__lastrep)
    
    def set_last_rep(self, value: str):
        self.__set(self.__lastrep, value)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return self.data

    def from_dict(self, data: Dict[str, Any]):
        self.data = data
        return self

    def __str__(self) -> str:
        return str(self.data)


    def get_rootdir(self) -> str:
        value = self.__get(self.__rootdir)
        return value
    
    def is_nerdfonts(self) -> bool:
        return self.__get(self.__nerdfonts)
    
    def set_nerdfonts(self, value: bool):
        self.__set(self.__nerdfonts, value)
        return self

    def set_rootdir(self, value: str):
        self.__set(self.__rootdir, value)
        return self

    def is_ascii(self):
        return self.__get(self.__is_ascii)

    def set_is_ascii(self, value: bool):
        self.__set(self.__is_ascii, value)
        return self

    def is_colored(self):
        return self.__get(self.__is_color)

    def set_is_colored(self, value: bool):
        self.__set(self.__is_color, value)
        return self
    
    def toggle_color(self):
        self.set_is_colored(not self.is_colored())
        return
    
    def toggle_nerdfonts(self):
        self.set_nerdfonts(not self.is_nerdfonts())
        return

    def get_diff_mode(self) -> str:
        return self.__get(self.__diffmode)

    def set_diff_mode(self, value: str):
        self.__set(self.__diffmode, value)
        return self

    def get_side_size(self):
        return self.__get(self.__sidesize)

    def set_side_size(self, value: int):
        self.__set(self.__sidesize, value)
        return self

    def get_lang_def(self):
        return self.__get(self.__langdef)

    def set_lang_def(self, value: str):
        self.__set(self.__langdef, value)
        return self
