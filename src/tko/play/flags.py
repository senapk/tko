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
    minimum = Flag().name("Mínimo").char("m").values(["0", "1"]).text("Mostra os requisitos mínimos para completar a missão").location("left")
    reward = Flag().name("Recompensa").char("r").values(["0", "1"]).text("Mostra a experiência obtida na tarefa").location("left")
    percent = Flag().name("Percentual").char("p").values(["0", "1"]).text("Mostra valores em porcentagem").location("left")
    admin = Flag().name("Admin").char("A").values(["0", "1"]).text("Mostra todas as missões e grupos").location("left")
    fortune = Flag().name("Conselho").char("C").values(["0", "1"]).text("Mostra mensagem aleatórias na saída").location("left")
    random = Flag().name("Sucesso").char("S").values(["1", "0"]).text("Mostra os personagens no sucesso da execução").location("left")
    config = Flag().name("Conf").char("c").values(["0", "1"]).text("Mostra a barra de flags").location("top")
    xpbar = Flag().name("XpBar").char("x").values(["0", "1"]).text("Mostra a barra de experiência").location("top")
    inventory = Flag().name("Inventário").char("i").values(["0", "1"]).text("Mostra a barra de skills").location("top")
    mono = Flag().name("Mono").char("M").values(["0", "1"]).text("Usa tema monocromatico").location("left")
    nerd = Flag().name("Nerd").char("n").values(["0", "1"]).text("Usa nerd fonts para habilitar bordas").location("left")

class FlagsMan:
    def __init__(self, data: Dict[str, int]):
        self.flags: Dict[str, Flag] = {}
        self.left: List[Flag] = []
        self.top: List[Flag] = []

        for varname, flag in Flags.__dict__.items():
            if isinstance(flag, Flag):
                self.flags[varname] = flag
                if flag.get_location() == "left":
                    self.left.append(flag)
                elif flag.get_location() == "top":
                    self.top.append(flag)

        for key, _index in data.items():
            if key in self.flags:
                self.flags[key].index(_index)

    def get_data(self) -> Dict[str, int]:
        data = {}
        for name, flag in self.flags.items():
            if len(flag.get_values()) > 1:
                data[name] = flag.get_index()
        return data
