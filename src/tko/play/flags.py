from typing import List, Dict, Any
from ..util.sentence import Sentence


class Flag:
    def __init__(self):
        self._name: str = ""
        self._text: str = ""  # description
        self._char: str = ""
        self._values: List[str] = ["0", "1"]
        self._index: int = 0
        self._location: str = ""
        self._bool = True  # many options

    def set_name(self, _name):
        self._name = _name
        return self

    def set_description(self, _text):
        self._text = _text
        return self

    def set_keycode(self, _key):
        self._char = _key
        return self

    def set_values(self, _values: List[str]):
        self._values = _values
        return self

    def index(self, _index):
        self._index = _index
        return self

    def location(self, value: str):
        self._location = value
        return self

    def get_values(self):
        return self._values

    def toggle(self):
        self._index = (self._index + 1) % len(self._values)
        return self
    
    def set_bool(self):
        self._bool = True
        return self
    
    def is_bool(self):
        return self._bool

    def get_location(self) -> str:
        return self._location

    def get_value(self) -> str:
        return self._values[self._index % len(self._values)]
    
    def set_value(self, value: Any):
        for i, v in enumerate(self._values):
            if v == value:
                self._index = i
                break

    def is_true(self):
        return self.get_value() == "1"

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._text

    def get_keycode(self) -> str:
        return self._char

    def get_index(self) -> int:
        return self._index
    

class Flags:
    minimum = Flag().set_name("Mínimo").set_keycode("M").set_values(["0", "1"])    .set_description("Mostra os requisitos para completar a missão").location("left")
    reward = Flag().set_name("Recompensa").set_keycode("R").set_values(["0", "1"]) .set_description("Mostra a experiência obtida nas tarefas     ").location("left")
    percent = Flag().set_name("Percentual").set_keycode("P").set_values(["1", "0"]).set_description("Mostra todos os valores em porcentagem      ").location("left")
    admin = Flag().set_name("Admin").set_keycode("A").set_values(["0", "1"])       .set_description("Habilitas todas as missões e tarefas        ").location("left")
    config    = Flag().set_name("Config").set_keycode("c").set_values(["0", "1"]).set_description("Mostra a barra de flags").location("top")
    skills = Flag().set_name("Skills").set_keycode("i").set_values(["0", "1"]).set_description("Mostra a barra de skills").location("top")

class FlagsMan:
    def __init__(self, data: Dict[str, int]):
        self.flags: Dict[str, Flag] = {}
        self.top: List[Flag] = []
        self.left: List[Flag] = []
        self.others: List[Flag] = []

        for varname, flag in Flags.__dict__.items():
            if isinstance(flag, Flag):
                self.flags[varname] = flag
                if flag.get_location() == "top":
                    self.top.append(flag)
                elif flag.get_location() == "left":
                    self.left.append(flag)
                else:
                    self.others.append(flag)

        for key, _index in data.items():
            if key in self.flags:
                self.flags[key].index(_index)

    def get_data(self) -> Dict[str, int]:
        data = {}
        for name, flag in self.flags.items():
            if flag.get_location() == "geral":
                continue
            if len(flag.get_values()) > 1:
                data[name] = flag.get_index()
        return data
