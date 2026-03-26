from __future__ import annotations
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
        self._autoload = True

    def set_autoload(self, value: bool):
        self._autoload = value
        return self
    
    def get_autoload(self) -> bool:
        return self._autoload

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

    def set_index(self, _index: int):
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
    panel_help = "0"
    panel_graph = "1"
    panel_logs = "2"
    panel_skills = "3"

    task_exec_view = "0"
    task_time_view = "1"
    
    inbox_only = "0"
    inbox_all = "1"

    panel = (Flag().set_name("Painel").set_description("Mostra o Painel de Informações")
                    .set_values([panel_help, panel_graph, panel_logs, panel_skills])
                    .set_msgs(["Mostrar ajuda", "Gráfico de tarefas", "Mostrar logs", "Mostrar trilhas de habilidades"]))
    inbox = (Flag().set_name("Tópicos").set_description("Habilitas todas as missões e tarefas")
                    .set_values([inbox_only, inbox_all])
                    .set_msgs(["Mostrar inbox", "Habilitar todas as tarefas"]))
    show_panel = (Flag().set_name("ShowPanel").set_description("Mostra o painel esquerdo")
                    .set_values(["0", "1"]).set_index(1)
                    .set_msgs(["Desabilitar painel lateral", "Mostrar painel lateral"]))
    task_graph_mode = (Flag().set_name("Task Graph").set_description("Mostra o Gráfico de Tarefas")
                    .set_values([task_exec_view, task_time_view])
                    .set_msgs(["Gráfico de tarefas por execuções", "Gráfico de tarefas por tempo"]))
    show_time = (Flag().set_name("Tempo").set_description("Mostra o tempo utilizado para completar as tarefas")
                    .set_values(["1", "0"])
                    .set_keycode(GuiKeys.show_duration)
                    .set_msgs(["Mostrar tempo gasto nas tarefas", "Ocultar tempo gasto nas tarefas"]))
class FlagsMan:
    def __init__(self, data: dict[str, int]):
        self.flags: dict[str, Flag] = {}

        for varname, flag in Flags.__dict__.items():
            if isinstance(flag, Flag):
                self.flags[varname] = flag

        for key, _index in data.items():
            if key in self.flags:
                self.flags[key].set_index(_index)

    def get_data(self) -> dict[str, int]:
        data: dict[str, int] = {}
        for name, flag in self.flags.items():
            if len(flag.get_values()) > 1:
                data[name] = flag.get_index()
        return data
