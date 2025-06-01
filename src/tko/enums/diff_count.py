import enum


class DiffCount(enum.Enum):
    FIRST = "MODO: APENAS PRIMEIRO ERRO"
    ALL   = "MODO: TODOS OS ERROS"
    NONE = "MODO: SILENCIOSO"