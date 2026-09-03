import enum


class TaskEval(enum.Enum):
    """Compatibilidade de API para consumidores antigos; o parser usa TaskType."""
    TEST = "test"
    SELF = "self"


class TaskType(enum.Enum):
    NULL = "null"
    WIKI = "wiki"  # material de consulta, sem avaliação
    SELF = "self"  # atividade com autoavaliação
    DIFF = "diff"  # atividade com testes de entrada/saída
    CODE = "code"  # reservado para testes programáticos

    # aliases de leitura para permitir a migração de índices antigos
    READ = WIKI
    MAKE = "make"

class Materialization(enum.Enum):
    LOCAL = "local"
    EXTERNAL = "external"
