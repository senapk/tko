from typing import Any
from tko.play.keys import GuiKeys

class Flag:
    def __init__(self):
        self._name: str = ""
        self._text: str = ""  # description
        self._msgs: list[str] = []
        self._char: str = ""
        self._values: list[str] = ["0", "1"]
        self._index: int = 0
        self._location: str = ""
        self._bool = True  # many options

    def set_name(self, _name: str):
        self._name = _name
        return self

    def set_description(self, _text: str):
        self._text = _text
        return self
    
    def get_msgs(self) -> list[str]:
        return self._msgs
    
    def set_msgs(self, msgs: list[str]):
        self._msgs = msgs
        return self

    def set_keycode(self, _key: str):
        self._char = _key
        return self

    def set_values(self, _values: list[str]):
        self._values = _values
        return self

    def index(self, _index: int):
        self._index = _index
        return self

    def get_values(self) -> list[str]:
        return self._values

    def toggle(self):
        self._index = (self._index + 1) % len(self._values)
        return None

    def get_value(self) -> str:
        return self._values[self._index % len(self._values)]
    
    def set_value(self, value: Any):
        for i, v in enumerate(self._values):
            if v == value:
                self._index = i
                break

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._text

    def get_keycode(self) -> str:
        return self._char

    def get_index(self) -> int:
        return self._index
    
    def is_true(self) -> bool:
        return self.get_value() != "0"
    
    def __bool__(self) -> bool:
        return self.get_value() == "1"
    

class Flags:
    quests = (Flag().set_name("Tópicos").set_keycode(GuiKeys.show_quests).set_description("Habilitas todas as missões e tarefas")
                    .set_values(["0", "1", "2"])
                    .set_msgs(["Mostrar apenas quests disponíveis", "Mostrar todas as quests sem habilitar", "Habilitar todas as quests"]))
    tracks = (Flag().set_name("Trilhas").set_keycode(GuiKeys.tracks).set_description("Mostra a barra de trilhas de habilidades")
                    .set_values(["0", "1", "2"])
                    .set_msgs(["Desabilitar painel de trilhas", "Mostrar painel de trilhas por porcentagem", "Mostrar painel de trilhas por xp"]))
    tasks = (Flag().set_name("Tarefas").set_keycode(GuiKeys.show_tasks).set_description("Mostra as atividades concluídas")
                    .set_values(["0", "1", "2"])
                    .set_msgs(["Mostrar todas as tarefas", "Ocultar tarefas com 100%", "Ocultar tarefas com >70%"]))
    graph = (Flag().set_name("Graph").set_keycode(GuiKeys.graph).set_description("Muda o Gráfico")
                    .set_values(["0", "1"])
                    .set_msgs(["Desabilitar gráficos de acompanhamento", "Mostrar gráficos de acompanhamento"]))
    xray = (Flag().set_name("X-Ray").set_keycode(GuiKeys.xray).set_description("Muda o modo X-Ray")
                    .set_values(["0", "1"])
                    .set_msgs(["Desabilitar modo X-Ray", "Ativar modo X-Ray"]))
class FlagsMan:
    def __init__(self, data: dict[str, int]):
        self.flags: dict[str, Flag] = {}

        for varname, flag in Flags.__dict__.items():
            if isinstance(flag, Flag):
                self.flags[varname] = flag

        for key, _index in data.items():
            if key in self.flags:
                self.flags[key].index(_index)

    def get_data(self) -> dict[str, int]:
        data: dict[str, int] = {}
        for name, flag in self.flags.items():
            if len(flag.get_values()) > 1:
                data[name] = flag.get_index()
        return data
