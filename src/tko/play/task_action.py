from enum import Enum

from tko.i18n import MsgKey, t


class _TaskActionMeta(type):
    _KEY_MAP: dict[str, Enum] = {
        "BAIXAR":   MsgKey("task_action.baixar"),
        "EXECUTAR": MsgKey("task_action.executar"),
        "VISITAR":  MsgKey("task_action.visitar"),
        "EXPANDIR": MsgKey("task_action.expandir"),
        "CONTRAIR": MsgKey("task_action.contrair"),
        "NENHUMA":  MsgKey("task_action.nenhuma"),
        "BLOQUEIO": MsgKey("task_action.bloqueio"),
    }

    def __getattr__(cls, name: str) -> str:
        key = cls._KEY_MAP.get(name)
        if key is not None:
            return t(key)
        raise AttributeError(name)


class TaskAction(metaclass=_TaskActionMeta):
    pass
