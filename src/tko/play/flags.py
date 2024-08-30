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

    def name(self, _name):
        self._name = _name
        return self

    def text(self, _text):
        self._text = _text
        return self

    def char(self, _key):
        self._char = _key
        return self

    def values(self, _values: List[str]):
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

    def many(self):
        self._bool = False
        return self
    
    def bool(self):
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

    def get_char(self) -> str:
        return self._char

    def get_index(self) -> int:
        return self._index
    

class Flags:
    minimum = Flag().name("Mínimo").char("M").values(["0", "1"]).text("Mostra os requisitos mínimos para completar a missão").location("left")
    reward = Flag().name("Recompensa").char("R").values(["0", "1"]).text("Mostra a experiência obtida na tarefa").location("left")
    percent = Flag().name("Percentual").char("P").values(["1", "0"]).text("Mostra valores em porcentagem").location("left")
    admin = Flag().name("Admin").char("A").values(["0", "1"]).text("Mostra todas as missões e grupos").location("left")
    # fortune = Flag().name("Fortuna").char("F").values(["0", "1"]).text("Mostra mensagem aleatórias na saída").location("left")
    images = Flag().name("Imagens").char("I").values(["1", "0"]).text("Mostra imagens aleatórias").location("left")
    # links = Flag().name("Links").char("Y").values(["0", "1"]).text("Mostra links remotos e locais das tarefas").location("left")

    config    = Flag().name("Config").char("c").values(["0", "1"]).text("Mostra a barra de flags").location("top")
    skills = Flag().name("Skills").char("i").values(["0", "1"]).text("Mostra a barra de skills").location("top")
    others = Flag().name("Outros").char("o").values(["0", "1"]).text("Mostra opções extras").location("bottom")

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
