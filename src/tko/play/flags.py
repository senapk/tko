from __future__ import annotations
from tko.play.keys import GuiKeys

class Flag:
    def __init__(self, id: str, default_value: str, msgs: dict[str, str], description: str, keycode: str | None = None):
        self.id = id
        self.default = default_value
        self._value: str = default_value
        self.msgs = msgs
        self.keycode = keycode
        self.description = description
    
    def get_value(self):
        if self._value not in self.msgs:
            return self.default
        return self._value
    
    def set_value(self, value: str):
        if value not in self.msgs:
            self._value = self.default
        else:
            self._value = value

    def toggle(self):
        keys = list(self.msgs.keys())
        index = keys.index(self.get_value())
        self._value = keys[(index + 1) % len(keys)]

class BoolFlag(Flag):
    TRUE = "true"
    FALSE = "false"

    def __init__(self, id: str, default_value: bool, msgs: dict[bool, str], description: str, keycode: str | None = None):
        super().__init__(
            id=id, 
            default_value=BoolFlag.TRUE if default_value else BoolFlag.FALSE, 
            msgs={
                BoolFlag.TRUE: msgs[True],
                BoolFlag.FALSE: msgs[False],
            }, 
            description=description,
            keycode=keycode
        )

    def is_true(self):
        return self.get_value() == BoolFlag.TRUE
    def set_true(self):
        self._value = BoolFlag.TRUE
    def set_false(self):
        self._value = BoolFlag.FALSE

class ViewMode(Flag):
    INBOX = "inbox"
    ALL = "all"

    def __init__(self, id: str):
        super().__init__(
            id=id,
            default_value=ViewMode.INBOX,
            msgs={
                ViewMode.INBOX: "Mostrar inbox",
                ViewMode.ALL: "Habilitar todas as tarefas",
            },
            description="Mostra inbox ou todas as atividades",
            keycode=""
        )

    def is_inbox(self):
        return self.get_value() == ViewMode.INBOX
    def is_all(self):
        return self.get_value() == ViewMode.ALL
    def set_view_inbox(self):
        self._value = ViewMode.INBOX
    def set_view_all(self):
        self._value = ViewMode.ALL

class PanelMode(Flag):
    HELP = "help"
    GRAPH = "graph"
    LOGS = "logs"
    SKILLS = "skills"
    def __init__(self, id: str, default_value: str):
        super().__init__(
            id=id,
            default_value=default_value,
            msgs={
                PanelMode.HELP: "Mostrar ajuda",
                PanelMode.GRAPH: "Gráfico de tarefas",
                PanelMode.LOGS: "Mostrar logs",
                PanelMode.SKILLS: "Mostrar trilhas",
            },
            description="Mostra o Painel de Informações",
            keycode=""
        )
    
    def is_help(self):
        return self.get_value() == PanelMode.HELP
    def is_graph(self):
        return self.get_value() == PanelMode.GRAPH
    def is_logs(self):
        return self.get_value() == PanelMode.LOGS
    def is_skills(self):
        return self.get_value() == PanelMode.SKILLS
    def set_help(self):
        self._value = PanelMode.HELP
    def set_graph(self):
        self._value = PanelMode.GRAPH
    def set_logs(self):
        self._value = PanelMode.LOGS
    def set_skills(self):
        self._value = PanelMode.SKILLS

class TaskGraphMode(Flag):
    EXEC = "executions"
    TIME = "time"

    def __init__(self, id: str):
        super().__init__(
            id=id,
            default_value=TaskGraphMode.EXEC,
            msgs={
                TaskGraphMode.EXEC: "Gráfico por execuções",
                TaskGraphMode.TIME: "Gráfico por tempo",
            },
            description="Modo do gráfico de tarefas",
            keycode=""
        )
    
    def is_executions(self):
        return self.get_value() == TaskGraphMode.EXEC
    def is_time_view(self):
        return self.get_value() == TaskGraphMode.TIME
    def set_exec_view(self):
        self._value = TaskGraphMode.EXEC
    def set_time_view(self):
        self._value = TaskGraphMode.TIME

class Flags:
    def __init__(self):
        self.task_view_mode = ViewMode("inbox")

        self.panel = PanelMode("panel", PanelMode.HELP)

        self.show_panel = BoolFlag(
            id="show_panel",
            default_value=True,
            msgs={
                True: "Mostrar painel lateral",
                False: "Ocultar painel lateral",
            },
            description="Mostra o painel lateral",
            keycode=""
        )

        self.task_graph_mode = TaskGraphMode("task_graph_mode")

        self.show_time = BoolFlag(
            id="show_time",
            default_value=True,
            msgs={
                True: "Mostrar tempo",
                False: "Ocultar tempo",
            },
            description="Mostra o tempo das tarefas",
            keycode= GuiKeys.show_duration
        )

        self.all_flags: list[Flag] = [
            self.task_view_mode,
            self.panel,
            self.show_panel,
            self.task_graph_mode,
            self.show_time,
        ]

    def to_dict(self) -> dict[str, str]:
        data: dict[str, str] = {
            self.task_view_mode.id: self.task_view_mode.get_value(),
            self.panel.id: self.panel.get_value(),
            self.show_panel.id: self.show_panel.get_value(),
            self.task_graph_mode.id: self.task_graph_mode.get_value(),
            self.show_time.id: self.show_time.get_value(),
        }
        return data


    def from_dict(self, data: dict[str, str]):
        self.task_view_mode.set_value(data.get(self.task_view_mode.id, self.task_view_mode.default))
        self.panel.set_value(data.get(self.panel.id, self.panel.default))
        self.show_panel.set_value(data.get(self.show_panel.id, self.show_panel.default))
        self.task_graph_mode.set_value(data.get(self.task_graph_mode.id, self.task_graph_mode.default))
        self.show_time.set_value(data.get(self.show_time.id, self.show_time.default))
