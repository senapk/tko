from typing import Any, Dict


class GeralSettings:
    __rootdir = "rootdir"
    __is_ascii = "ascii"
    __is_color = "color"
    __diffdown = "diffdown"
    __sidesize = "sidesize"
    __langdef = "lang"

    defaults = {
        __rootdir: "",
        __is_ascii: False,
        __is_color: True,
        __diffdown: True,
        __sidesize: 80,
        __langdef: ""
    }

    def __init__(self):
        self.data: Dict[str, Any] = {}
        for key in GeralSettings.defaults:
            self.data[key] = GeralSettings.defaults[key]

    def __set(self, key: str, value: Any):
        self.data[key] = value
        return self
    
    def __get(self, key: str) -> str:
        if key not in self.defaults:
            raise ValueError(f"Key {key} not found in GeralSettings")
        return self.data.get(key, GeralSettings.defaults[key])
        

    def to_dict(self) -> Dict[str, Any]:
        return self.data
        
    def from_dict(self, data: Dict[str, Any]):
        self.data = data
        return self

    def __str__(self) -> str:
        return str(self.data)


    def get_rootdir(self) -> str:
        return self.__get(self.__rootdir)
    
    def set_rootdir(self, value: str):
        self.__set(self.__rootdir, value)
        return self
    
    def get_is_ascii(self):
        return self.__get(self.__is_ascii)

    def set_is_ascii(self, value: bool):
        self.__set(self.__is_ascii, value)
        return self
    
    def get_is_colored(self):
        return self.__get(self.__is_color)
    
    def set_is_colored(self, value: bool):
        self.__set(self.__is_color, value)
        return self
    
    def get_is_diff_down(self):
        return self.__get(self.__diffdown)
    
    def set_is_diff_down(self, value: bool):
        self.__set(self.__diffdown, value)
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
    
