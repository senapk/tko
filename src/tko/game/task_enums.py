import enum


class EvalMode(enum.Enum):
    NONE = "none"  # material de consulta, sem avaliação
    SELF = "self"  # atividade com autoavaliação
    DIFF = "diff"  # atividade com testes de entrada/saída

class Materialization(enum.Enum):
    LOCAL = "local"
    EXTERNAL = "external"
